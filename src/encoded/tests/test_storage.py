import pytest
pytestmark = pytest.mark.storage


def test_storage_creation(session):
    from encoded.storage import (
        Statement,
        CurrentStatement,
        TransactionRecord,
        Blob,
        Key,
        UserMap
    )
    assert session.query(Statement).count() == 0
    assert session.query(CurrentStatement).count() == 0
    assert session.query(TransactionRecord).count() == 0
    assert session.query(Blob).count() == 0
    assert session.query(Key).count() == 0
    assert session.query(UserMap).count() == 0


def test_transaction_record(session):
    from encoded.storage import (
        Resource,
        Statement,
        TransactionRecord,
    )
    predicate = 'testdata'
    obj1 = {'foo': 'bar'}
    resource = Resource()
    session.add(resource)
    stmt = Statement(predicate=predicate, object=obj1, rid=resource.rid)
    session.add(stmt)
    session.flush()
    assert session.query(Statement).count() == 1
    statement = session.query(Statement).one()
    assert session.query(TransactionRecord).count() == 1
    record = session.query(TransactionRecord).one()
    assert record.tid
    assert statement.tid == record.tid


def test_current_statement(session):
    from encoded.storage import (
        CurrentStatement,
        Resource,
        Statement,
        TransactionRecord,
    )
    predicate = 'testdata'
    obj1 = {'foo': 'bar'}
    resource = Resource({predicate: obj1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()
    assert resource.rid
    assert resource[predicate] == obj1
    statement = session.query(Statement).one()
    assert statement.sid
    assert statement.rid == resource.rid
    current = session.query(CurrentStatement).one()
    assert current.sid == statement.sid
    assert current.rid == resource.rid
    record = session.query(TransactionRecord).one()
    assert record.tid
    assert statement.tid == record.tid


def test_current_statement_update(session):
    from encoded.storage import (
        CurrentStatement,
        Resource,
        Statement,
    )
    predicate = 'testdata'
    obj1 = {'foo': 'bar'}
    resource = Resource({predicate: obj1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()
    obj2 = {'foo': 'baz'}
    resource[predicate] = obj2
    session.flush()
    resource = session.query(Resource).one()
    session.flush()
    assert resource[predicate] == obj2
    assert session.query(Statement).count() == 2
    assert [stmt.object for stmt in resource.data[predicate].history] == [obj1, obj2]
    current = session.query(CurrentStatement).one()
    assert current.sid


def test_keys(session):
    from sqlalchemy.orm.exc import FlushError
    from encoded.storage import (
        Resource,
        Key,
    )
    predicate = 'testdata'
    obj1 = {'foo': 'bar'}
    resource = Resource({predicate: obj1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()

    testname = 'foo'
    key = Key(rid=resource.rid, namespace=predicate, name=testname, value=obj1[testname])
    session.add(key)
    session.flush()
    assert session.query(Key).count() == 1
    othertest = 'foofoo'
    othervalue = 'barbar'
    key2 = Key(rid=resource.rid, namespace=predicate, name=othertest, value=othervalue)
    session.add(key2)
    session.flush()
    assert session.query(Key).count() == 2
    obj2 = {'foofoo': 'barbar'}
    resource2 = Resource({predicate: obj2})
    session.add(resource2)
    session.flush()
    key3 = Key(rid=resource2.rid, namespace=predicate, name=testname, value=obj1[testname])
    session.add(key3)
    with pytest.raises(FlushError):
        session.flush()
