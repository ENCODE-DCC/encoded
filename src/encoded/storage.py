from past.builtins import basestring
from pyramid.httpexceptions import HTTPConflict
from sqlalchemy import (
    Column,
    DDL,
    ForeignKey,
    bindparam,
    event,
    func,
    null,
    orm,
    schema,
    types,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import collections
from sqlalchemy.orm.exc import (
    FlushError,
    NoResultFound,
)
from .precompiled_query import (
    PrecompiledQuery,
    precompiled_query_builder,
)
from .renderers import json_renderer
import json
import transaction
import uuid
import zope.sqlalchemy

DBSession = orm.scoped_session(orm.sessionmaker(query_cls=PrecompiledQuery))
zope.sqlalchemy.register(DBSession)
Base = declarative_base()


def _get_by_uuid_instance_map(rid):
    # Internals from sqlalchemy/orm/query.py:Query.get
    session = DBSession()
    mapper = orm.class_mapper(Resource)
    ident = [rid]
    key = mapper.identity_key_from_primary_key(ident)
    return orm.loading.get_from_identity(
        session, key, orm.attributes.PASSIVE_OFF)


@precompiled_query_builder(DBSession)
def _get_by_uuid_query():
    session = DBSession()
    return session.query(Resource).filter(Resource.rid == bindparam('rid'))


@precompiled_query_builder(DBSession)
def _get_by_unique_key_query():
    session = DBSession()
    return session.query(Key).options(
        orm.joinedload_all(
            Key.resource,
            Resource.data,
            CurrentPropertySheet.propsheet,
            innerjoin=True,
        ),
    ).filter(Key.name == bindparam('name'), Key.value == bindparam('value'))


class RDBStorage(object):
    def get_by_uuid(self, rid, default=None):
        if isinstance(rid, basestring):
            try:
                rid = uuid.UUID(rid)
            except ValueError:
                return default
        elif not isinstance(rid, uuid.UUID):
            raise TypeError(rid)

        model = _get_by_uuid_instance_map(rid)

        if model is None:
            try:
                model = _get_by_uuid_query().params(rid=rid).one()
            except NoResultFound:
                return default

        return model

    def get_by_unique_key(self, unique_key, name, default=None):
        try:
            key = _get_by_unique_key_query().params(name=unique_key, value=name).one()
        except NoResultFound:
            return default
        else:
            return key.resource

    def __iter__(self, item_type=None, batchsize=1000):
        session = DBSession()
        query = session.query(Resource.rid)

        if item_type is not None:
            query = query.filter(
                Resource.item_type == item_type
            )

        for rid, in query.yield_per(batchsize):
            yield rid

    def __len__(self, item_type=None):
        session = DBSession()
        query = session.query(Resource.rid)
        if item_type is not None:
            query = query.filter(
                Resource.item_type == item_type
            )
        return query.count()

    def create(self, item_type, rid):
        return Resource(item_type, rid=rid)

    def update(self, model, properties=None, sheets=None, unique_keys=None, links=None):
        session = DBSession()
        sp = session.begin_nested()
        try:
            session.add(model)
            update_properties(model, properties, sheets)
            if links is not None:
                update_rels(model, links)
            if unique_keys is not None:
                keys_add, keys_remove = update_keys(model, unique_keys)
            sp.commit()
        except (IntegrityError, FlushError):
            sp.rollback()
        else:
            return

        # Try again more carefully
        try:
            session.add(model)
            update_properties(model, properties, sheets)
            if links is not None:
                update_rels(model, links)
            session.flush()
        except (IntegrityError, FlushError):
            msg = 'UUID conflict'
            raise HTTPConflict(msg)
        assert unique_keys is not None
        conflicts = check_duplicate_keys(model, keys_add)
        assert conflicts
        msg = 'Keys conflict: %r' % conflicts
        raise HTTPConflict(msg)


def update_properties(model, properties, sheets=None):
    if properties is not None:
        model.propsheets[''] = properties
    if sheets is not None:
        for key, value in sheets.items():
            model.propsheets[key] = value


def update_keys(model, unique_keys):
    keys_set = {(k, v) for k, values in unique_keys.items() for v in values}

    existing = {
        (key.name, key.value)
        for key in model.unique_keys
    }

    to_remove = existing - keys_set
    to_add = keys_set - existing

    session = DBSession()
    for pk in to_remove:
        key = session.query(Key).get(pk)
        session.delete(key)

    for name, value in to_add:
        key = Key(rid=model.rid, name=name, value=value)
        session.add(key)

    return to_add, to_remove


def check_duplicate_keys(model, keys):
    session = DBSession()
    return [pk for pk in keys if session.query(Key).get(pk) is not None]


def update_rels(model, links):
    session = DBSession()
    source = model.rid

    rels = {(k, uuid.UUID(target)) for k, targets in links.items() for target in targets}

    existing = {
        (link.rel, link.target_rid)
        for link in model.rels
    }

    to_remove = existing - rels
    to_add = rels - existing

    for rel, target in to_remove:
        link = session.query(Link).get((source, rel, target))
        session.delete(link)

    for rel, target in to_add:
        link = Link(source_rid=source, rel=rel, target_rid=target)
        session.add(link)

    return to_add, to_remove


class UUID(types.TypeDecorator):
    """Platform-independent UUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = types.CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(types.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            else:
                return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class JSON(types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = types.Text
    using_native_json = False

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            if dialect.server_version_info >= (9, 4):
                self.using_native_json = True
                return dialect.type_descriptor(postgresql.JSONB())
            if dialect.server_version_info >= (9, 2):
                self.using_native_json = True
                return dialect.type_descriptor(postgresql.JSON())
        return dialect.type_descriptor(types.Text())

    def process_bind_param(self, value, dialect):
        if self.using_native_json:
            return value
        if value is None:
            return value
        return json_renderer.dumps(value)

    def process_result_value(self, value, dialect):
        if self.using_native_json:
            return value
        if value is None:
            return value
        return json.loads(value)


class Key(Base):
    ''' indexed unique tables for accessions and other unique keys
    '''
    __tablename__ = 'keys'

    # typically the field that is unique, i.e. accession
    # might be prefixed with a namespace for per name unique values
    name = Column(types.String, primary_key=True)
    # the unique value
    value = Column(types.String, primary_key=True)

    rid = Column(UUID, ForeignKey('resources.rid'),
                 nullable=False, index=True)

    # Be explicit about dependencies to the ORM layer
    resource = orm.relationship('Resource', backref='unique_keys')


class Link(Base):
    """ indexed relations
    """
    __tablename__ = 'links'
    source_rid = Column(
        'source', UUID, ForeignKey('resources.rid'), primary_key=True)
    rel = Column(types.String, primary_key=True)
    target_rid = Column(
        'target', UUID, ForeignKey('resources.rid'), primary_key=True,
        index=True)  # Single column index for reverse lookup

    source = orm.relationship(
        'Resource', foreign_keys=[source_rid], backref='rels')
    target = orm.relationship(
        'Resource', foreign_keys=[target_rid], backref='revs')


class PropertySheet(Base):
    '''A triple describing a resource
    '''
    __tablename__ = 'propsheets'
    __table_args__ = (
        schema.ForeignKeyConstraint(
            ['rid', 'name'],
            ['current_propsheets.rid', 'current_propsheets.name'],
            name='fk_property_sheets_rid_name', use_alter=True,
            deferrable=True, initially='DEFERRED',
        ),
    )
    # The sid column also serves as the order.
    sid = Column(types.Integer, autoincrement=True, primary_key=True)
    rid = Column(UUID,
                 ForeignKey('resources.rid',
                            deferrable=True,
                            initially='DEFERRED'),
                 nullable=False)
    name = Column(types.String, nullable=False)
    properties = Column(JSON)
    tid = Column(UUID,
                 ForeignKey('transactions.tid',
                            deferrable=True,
                            initially='DEFERRED'),
                 nullable=False)
    resource = orm.relationship('Resource')
    transaction = orm.relationship('TransactionRecord')


class CurrentPropertySheet(Base):
    __tablename__ = 'current_propsheets'
    rid = Column(UUID, ForeignKey('resources.rid'),
                 nullable=False, primary_key=True)
    name = Column(types.String, nullable=False, primary_key=True)
    sid = Column(types.Integer,
                 ForeignKey('propsheets.sid'), nullable=False)
    propsheet = orm.relationship(
        'PropertySheet', lazy='joined', innerjoin=True,
        primaryjoin="CurrentPropertySheet.sid==PropertySheet.sid",
    )
    history = orm.relationship(
        'PropertySheet', order_by=PropertySheet.sid,
        post_update=True,  # Break cyclic dependency
        primaryjoin="""and_(CurrentPropertySheet.rid==PropertySheet.rid,
                    CurrentPropertySheet.name==PropertySheet.name)""",
    )
    resource = orm.relationship('Resource')


class Resource(Base):
    '''Resources are described by multiple propsheets
    '''
    __tablename__ = 'resources'
    rid = Column(UUID, primary_key=True)
    item_type = Column(types.String, nullable=False)
    data = orm.relationship(
        'CurrentPropertySheet', cascade='all, delete-orphan',
        innerjoin=True, lazy='joined',
        collection_class=collections.attribute_mapped_collection('name'),
    )

    def __init__(self, item_type, data=None, rid=None):
        if rid is None:
            rid = uuid.uuid4()
        super(Resource, self).__init__(item_type=item_type, rid=rid)
        if data is not None:
            for k, v in data.items():
                self.propsheets[k] = v

    def __getitem__(self, key):
        return self.data[key].propsheet.properties

    def __setitem__(self, key, value):
        current = self.data.get(key, None)
        if current is None:
            self.data[key] = current = CurrentPropertySheet(name=key, rid=self.rid)
        propsheet = PropertySheet(name=key, properties=value, rid=self.rid)
        current.propsheet = propsheet

    def keys(self):
        return self.data.keys()

    def get(self, key, default=None):
        try:
            return self.propsheets[key]
        except KeyError:
            return default

    @property
    def properties(self):
        return self.propsheets['']

    @property
    def propsheets(self):
        return self

    @property
    def uuid(self):
        return self.rid

    @property
    def tid(self):
        return self.data[''].propsheet.tid


class Blob(Base):
    """ Binary data
    """
    __tablename__ = 'blobs'
    blob_id = Column(UUID, primary_key=True)
    data = Column(types.LargeBinary)


class TransactionRecord(Base):
    __tablename__ = 'transactions'
    order = Column(types.Integer, autoincrement=True, primary_key=True)
    tid = Column(UUID, default=uuid.uuid4, nullable=False, unique=True)
    data = Column(JSON)
    timestamp = Column(
        types.DateTime(timezone=True), nullable=False, server_default=func.now())
    # A server_default is necessary for the notify_ddl overwrite to work
    xid = Column(types.BigInteger, nullable=True, server_default=null())
    __mapper_args__ = {
        'eager_defaults': True,
    }


notify_ddl = DDL("""
    ALTER TABLE %(table)s ALTER COLUMN "xid" SET DEFAULT txid_current();
    CREATE OR REPLACE FUNCTION encoded_transaction_notify() RETURNS trigger AS $$
    DECLARE
    BEGIN
        PERFORM pg_notify('encoded.transaction', NEW.xid::TEXT);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER encoded_transactions_insert AFTER INSERT ON %(table)s
    FOR EACH ROW EXECUTE PROCEDURE encoded_transaction_notify();
""")

event.listen(
    TransactionRecord.__table__, 'after_create',
    notify_ddl.execute_if(dialect='postgresql'),
)


@event.listens_for(PropertySheet, 'before_insert')
def set_tid(mapper, connection, target):
    if target.tid is not None:
        return
    txn = transaction.get()
    data = txn._extension
    target.tid = data['tid']


@event.listens_for(DBSession, 'before_flush')
def add_transaction_record(session, flush_context, instances):
    txn = transaction.get()
    # Set data with txn.setExtendedInfo(name, value)
    data = txn._extension
    record = data.get('_encoded_transaction_record')
    if record is not None:
        if orm.object_session(record) is None:
            # Savepoint rolled back
            session.add(record)
        # Transaction has already been recorded
        return

    tid = data['tid'] = uuid.uuid4()
    record = TransactionRecord(tid=tid)
    data['_encoded_transaction_record'] = record
    session.add(record)


@event.listens_for(DBSession, 'before_commit')
def record_transaction_data(session):
    txn = transaction.get()
    data = txn._extension
    if '_encoded_transaction_record' not in data:
        return

    record = data['_encoded_transaction_record']

    # txn.note(text)
    if txn.description:
        data['description'] = txn.description

    # txn.setUser(user_name, path='/') -> '/ user_name'
    # Set by pyramid_tm as (userid, '')
    if txn.user:
        user_path, userid = txn.user.split(' ', 1)
        data['userid'] = userid

    record.data = {k: v for k, v in data.items() if not k.startswith('_')}
    session.add(record)


@event.listens_for(DBSession, 'after_begin')
def read_only_doomed_transaction(session, sqla_txn, connection):
    ''' Doomed transactions can be read-only.

    ``transaction.doom()`` must be called before the connection is used.
    '''
    if not transaction.isDoomed():
        return
    if connection.engine.url.drivername != 'postgresql':
        return
    connection.execute("SET TRANSACTION READ ONLY;")
