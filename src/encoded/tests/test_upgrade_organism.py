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


def test_organism_upgrade(upgrader, organism_1):
    value = upgrader.upgrade('organism', organism_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
