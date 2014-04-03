import pytest


@pytest.fixture
def access_key(submitter):
    return{
        'user': submitter['uuid']
    }


@pytest.fixture
def access_key_1(access_key):
    item = access_key.copy()
    item.update({
        'schema_version': '1'
    })
    return item


def test_access_key_upgrade(app, access_key_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('access_key', access_key_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'