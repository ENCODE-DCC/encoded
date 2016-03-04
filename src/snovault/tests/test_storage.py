import pytest
pytestmark = pytest.mark.storage


def test_storage_creation(session):
    from snovault.storage import (
        PropertySheet,
        CurrentPropertySheet,
        TransactionRecord,
        Blob,
        Key,
        Link,
    )
    assert session.query(PropertySheet).count() == 0
    assert session.query(CurrentPropertySheet).count() == 0
    assert session.query(TransactionRecord).count() == 0
    assert session.query(Blob).count() == 0
    assert session.query(Key).count() == 0
    assert session.query(Link).count() == 0


def test_transaction_record(session):
    from snovault.storage import (
        Resource,
        PropertySheet,
        TransactionRecord,
    )
    name = 'testdata'
    props1 = {'foo': 'bar'}
    resource = Resource('test_item')
    session.add(resource)
    propsheet = PropertySheet(name=name, properties=props1, rid=resource.rid)
    session.add(propsheet)
    session.flush()
    assert session.query(PropertySheet).count() == 1
    propsheet = session.query(PropertySheet).one()
    assert session.query(TransactionRecord).count() == 1
    record = session.query(TransactionRecord).one()
    assert record.tid
    assert propsheet.tid == record.tid


def test_transaction_record_rollback(session):
    import transaction
    import uuid
    from snovault.storage import Resource
    rid = uuid.uuid4()
    resource = Resource('test_item', {'': {}}, rid=rid)
    session.add(resource)
    transaction.commit()
    transaction.begin()
    sp = session.begin_nested()
    resource = Resource('test_item', {'': {}}, rid=rid)
    session.add(resource)
    with pytest.raises(Exception):
        sp.commit()
    sp.rollback()
    resource = Resource('test_item', {'': {}})
    session.add(resource)
    transaction.commit()


def test_current_propsheet(session):
    from snovault.storage import (
        CurrentPropertySheet,
        Resource,
        PropertySheet,
        TransactionRecord,
    )
    name = 'testdata'
    props1 = {'foo': 'bar'}
    resource = Resource('test_item', {name: props1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()
    assert resource.rid
    assert resource[name] == props1
    propsheet = session.query(PropertySheet).one()
    assert propsheet.sid
    assert propsheet.rid == resource.rid
    current = session.query(CurrentPropertySheet).one()
    assert current.sid == propsheet.sid
    assert current.rid == resource.rid
    record = session.query(TransactionRecord).one()
    assert record.tid
    assert propsheet.tid == record.tid


def test_current_propsheet_update(session):
    from snovault.storage import (
        CurrentPropertySheet,
        Resource,
        PropertySheet,
    )
    name = 'testdata'
    props1 = {'foo': 'bar'}
    resource = Resource('test_item', {name: props1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()
    props2 = {'foo': 'baz'}
    resource[name] = props2
    session.flush()
    resource = session.query(Resource).one()
    session.flush()
    assert resource[name] == props2
    assert session.query(PropertySheet).count() == 2
    assert [propsheet.properties for propsheet in resource.data[name].history] == [props1, props2]
    current = session.query(CurrentPropertySheet).one()
    assert current.sid


def test_keys(session):
    from sqlalchemy.orm.exc import FlushError
    from snovault.storage import (
        Resource,
        Key,
    )
    name = 'testdata'
    props1 = {'foo': 'bar'}
    resource = Resource('test_item', {name: props1})
    session.add(resource)
    session.flush()
    resource = session.query(Resource).one()

    testname = 'foo'
    key = Key(rid=resource.rid, name=testname, value=props1[testname])
    session.add(key)
    session.flush()
    assert session.query(Key).count() == 1
    othertest = 'foofoo'
    othervalue = 'barbar'
    key2 = Key(rid=resource.rid, name=othertest, value=othervalue)
    session.add(key2)
    session.flush()
    assert session.query(Key).count() == 2
    props2 = {'foofoo': 'barbar'}
    resource2 = Resource('test_item', {name: props2})
    session.add(resource2)
    session.flush()
    key3 = Key(rid=resource2.rid, name=testname, value=props1[testname])
    session.add(key3)
    with pytest.raises(FlushError):
        session.flush()


def test_S3BlobStorage(mocker):
    from snovault.storage import S3BlobStorage
    mocker.patch('boto.connect_s3')
    bucket = 'test'
    fake_key = mocker.Mock()
    storage = S3BlobStorage(bucket)
    storage.bucket.name = bucket
    storage.bucket.new_key.return_value = fake_key

    download_meta = {'download': 'test.txt'}
    storage.store_blob('data', download_meta)
    assert download_meta['bucket'] == 'test'
    assert 'key' in download_meta
    fake_key.set_contents_from_string.assert_called_once_with('data')

    storage.bucket.get_key.return_value = fake_key
    fake_key.get_contents_as_string.return_value = 'data'
    data = storage.get_blob(download_meta)
    assert data == 'data'
    storage.bucket.get_key.assert_called_once_with(download_meta['key'], validate=False)

    storage.read_conn.generate_url.return_value = 'http://testurl'
    url = storage.get_blob_url(download_meta)
    assert url == 'http://testurl'
    storage.read_conn.generate_url.assert_called_once_with(
        129600, method='GET', bucket='test', key=download_meta['key']
    )


def test_S3BlobStorage_get_blob_url_for_non_s3_file(mocker):
    from snovault.storage import S3BlobStorage
    mocker.patch('boto.connect_s3')
    bucket = 'test'
    storage = S3BlobStorage(bucket)
    storage.bucket.name = bucket
    download_meta = {'blob_id': 'blob_id'}
    storage.read_conn.generate_url.return_value = 'http://testurl'
    url = storage.get_blob_url(download_meta)
    assert url == 'http://testurl'
    storage.read_conn.generate_url.assert_called_once_with(
        129600, method='GET', bucket='test', key=download_meta['blob_id']
    )
