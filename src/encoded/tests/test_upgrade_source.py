import pytest


@pytest.fixture
def source():
    return{
        'title': 'Fake source',
        'name': "fake-source"
    }


@pytest.fixture
def source_1(source):
    item = source.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


def test_source_upgrade(app, source_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('source', source_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
