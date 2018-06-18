import pytest


@pytest.fixture
def organism():
    return{
        'name': 'mouse',
        'taxon_id': '9031'
    }


@pytest.fixture
def organism_1(organism):
    item = organism.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def organism_4(organism):
    item = organism.copy()
    item.update({
        'schema_version': '4',
        'status': 'current',
    })
    return item


def test_organism_upgrade(upgrader, organism_1):
    value = upgrader.upgrade('organism', organism_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_organism_upgrade_4_5(upgrader, organism_4):
    value = upgrader.upgrade('organism', organism_4, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'released'
    organism_4['status'] = 'disabled'
    organism_4['schema_version'] = '4'
    value = upgrader.upgrade('organism', organism_4, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'deleted'
