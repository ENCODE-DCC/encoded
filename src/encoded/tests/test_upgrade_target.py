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

@pytest.fixture
def target_2(target):
    item = target.copy()
    item.update({
        'schema_version': '2',
        'uuid': '96f97790-3853-11e4-916c-0800200c9a66'
    })
    return item

def test_target_upgrade(app, target_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('target', target_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_target_investigated_as_upgrade(app, target_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['transcription factor']


def test_target_investigated_as_upgrade_tag(app, target_2):
    migrator = app.registry['migrator']
    target_2['uuid'] = '59c3efe9-00c6-4b1b-858b-5a208478972c'
    value = migrator.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['tag']

def test_target_investigated_as_upgrade_recombinant(app, target_2):
    migrator = app.registry['migrator']
    target_2['label'] = 'eGFP-test'
    value = migrator.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['recombinant protein', 'transcription factor']
