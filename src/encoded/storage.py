from UserDict import DictMixin
from sqlalchemy import (
    Column,
    DDL,
    ForeignKey,
    event,
    func,
    null,
    orm,
    schema,
    types,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import collections
from zope.sqlalchemy import ZopeTransactionExtension
from .renderers import json_renderer
import json
import transaction
import uuid

DBSession = orm.scoped_session(orm.sessionmaker(
    extension=ZopeTransactionExtension(),
    weak_identity_map=False,
))
Base = declarative_base()


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


class PGJSON(types.Text):
    """Postgresql JSON type.
    """
    __visit_name__ = 'JSON'


@compiles(PGJSON, 'postgresql')
def compile_varchar(element, compiler, **kw):
    return 'JSON'


class JSON(types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = types.Text

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGJSON())
        else:
            return dialect.type_descriptor(types.Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return json_renderer.dumps(value)

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = json.loads(value)
        return value


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


class Resource(Base, DictMixin):
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
            self.update(data)

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
        types.DateTime, nullable=False, server_default=func.now())
    # A server_default is necessary for the notify_ddl overwrite to work
    xid = Column(types.BigInteger, nullable=True, server_default=null())


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
    if 'tid' in data:
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
    del data['_encoded_transaction_record']

    # txn.note(text)
    if txn.description:
        data['description'] = txn.description

    # txn.setUser(user_name, path='/') -> '/ user_name'
    # Set by pyramid_tm as (userid, '')
    if txn.user:
        user_path, userid = txn.user.split(' ', 1)
        data['userid'] = userid

    record.data = data.copy()
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
