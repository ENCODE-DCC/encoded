from UserDict import DictMixin
from sqlalchemy import (
    Column,
    ForeignKey,
    event,
    func,
    orm,
    schema,
    types,
    )
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import collections
from zope.sqlalchemy import ZopeTransactionExtension
from .renderers import json_renderer
import json
import transaction
import uuid

DBSession = orm.scoped_session(orm.sessionmaker(
    extension=ZopeTransactionExtension(),
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
        if value is not None:
            value = json.loads(value)
        return value


class Statement(Base):
    '''A triple describing a resource
    '''
    __tablename__ = 'statements'
    __table_args__ = (
        schema.ForeignKeyConstraint(['rid', 'predicate'],
            ['current_statements.rid', 'current_statements.predicate'],
            name='fk_statements_rid_predicate', use_alter=True,
            deferrable=True, initially='DEFERRED',
            ),
        )
    # The sid column also serves as the order.
    sid = Column(types.Integer, autoincrement=True, primary_key=True)
    rid = Column(UUID, ForeignKey('resources.rid'), nullable=False)
    predicate = Column(types.String, nullable=False)
    object = Column(JSON)
    tid = Column(UUID, ForeignKey('transactions.tid'), nullable=False)
    resource = orm.relationship('Resource')
    transaction = orm.relationship('TransactionRecord')

    def __json__(self, request=None):
        return self.object


class CurrentStatement(Base):
    __tablename__ = 'current_statements'
    rid = Column(UUID, ForeignKey('resources.rid'),
        nullable=False, primary_key=True)
    predicate = Column(types.String, nullable=False, primary_key=True)
    sid = Column(types.Integer,
        ForeignKey('statements.sid'),
        nullable=False)
    statement = orm.relationship('Statement',
        lazy='joined',
        primaryjoin="CurrentStatement.sid==Statement.sid")
    history = orm.relationship('Statement',
        primaryjoin="""and_(CurrentStatement.rid==Statement.rid,
            CurrentStatement.predicate==Statement.predicate)""",
        order_by=Statement.sid)
    resource = orm.relationship('Resource')


class Resource(Base, DictMixin):
    '''Resources are described by multiple statements
    '''
    __tablename__ = 'resources'
    rid = Column(UUID, primary_key=True)
    data = orm.relationship('CurrentStatement',
        collection_class=collections.attribute_mapped_collection('predicate'),
        cascade='all, delete-orphan',
        )

    def __init__(self, data=None, rid=None):
        if rid is None:
            rid = uuid.uuid4()
        super(Resource, self).__init__(rid=rid)
        if data is not None:
            self.update(data)

    def __getitem__(self, key):
        return self.data[key].statement.object

    def __setitem__(self, key, value):
        current = self.data.get(key, None)
        if current is None:
            self.data[key] = current = CurrentStatement(predicate=key, rid=self.rid)
        statement = Statement(predicate=key, object=value, rid=self.rid)
        current.statement = statement

    def keys(self):
        return self.data.keys()


class TransactionRecord(Base):
    __tablename__ = 'transactions'
    tid = Column(UUID, default=uuid.uuid4, primary_key=True)
    data = Column(JSON)
    timestamp = Column(types.DateTime,
        nullable=False, server_default=func.now())


class UserMap(Base):
    __tablename__ = 'user_map'
    # e.g. mailto:test@example.com
    login = Column(types.Text, primary_key=True)
    userid = Column(UUID, ForeignKey('resources.rid'), nullable=False)

    resource = orm.relationship('Resource',
        lazy='joined', foreign_keys=[userid])

    user = orm.relationship('CurrentStatement',
        lazy='joined', foreign_keys=[userid],
        primaryjoin="""and_(CurrentStatement.rid==UserMap.userid,
            CurrentStatement.predicate=='user')""")

    # might have to be deferred

    def __init__(self, login, userid):
        self.login = login
        self.userid = userid


@event.listens_for(Statement, 'before_insert')
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
    # txn.note(text)
    if txn.description:
        data['description'] = txn.description
    # txn.setUser(user_name, path='/') -> 'user_name /'
    if txn.user:
        data['user'] = txn.user
    tid = data['tid'] = uuid.uuid4()
    record = TransactionRecord(tid=tid, data=data)
    session.add(record)
