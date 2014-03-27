import pytest


@pytest.fixture
def replicate(experiment):
    return {
         'experiment': experiment['uuid'],
         'biological_replicate_number': 1,
         'technical_replicate_number': 1,
    }


@pytest.fixture
def replicate_rbns(replicate):
    item = replicate.copy()
    item.update ({
         'RBNS_protein_concentration': 10,
         'RBNS_protein_concentration_units': 'nM',
    })
    return item


@pytest.fixture
def replicate_rbns_no_units(replicate):
    item = replicate.copy()
    item.update ({
         'RBNS_protein_concentration': 10,
    })
    return item


def test_replicate_rbns_post(testapp, replicate_rbns):
   testapp.post_json('/replicate', replicate_rbns)


def test_replicate_rbns_unit_requirement(testapp, replicate_rbns_no_units):
   testapp.post_json('/replicate', replicate_rbns_no_units, status=422)
