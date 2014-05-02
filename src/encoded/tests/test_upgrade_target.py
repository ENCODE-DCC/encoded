import pytest


@pytest.fixture
def target(organism):
    return{
        'organism': organism['uuid'],
        'label': 'TEST'
    }


@pytest.fixture
def target_1(target):
    item = target.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


def test_target_upgrade(app, target_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('target', target_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
