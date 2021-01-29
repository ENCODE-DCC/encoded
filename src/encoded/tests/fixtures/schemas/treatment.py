import pytest


@pytest.fixture
def treatment():
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }


@pytest.fixture
def treatment_5(testapp, organism):
    item = {
        'treatment_term_name': 'ethanol',
        'treatment_type': 'chemical'
    }
    return testapp.post_json('/treatment', item).json['@graph'][0]


@pytest.fixture
def treatment_2(treatment_0_0):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def submitter_treatment(submitter, lab):
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965',
        'submitted_by': submitter['@id']
    }

@pytest.fixture
def treatment_0_0():
    return{
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }


@pytest.fixture
def treatment_1(treatment_0_0, award):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['Estradiol_1nM'],
        'award': award['uuid'],
    })
    return item


@pytest.fixture
def treatment_3(treatment_0_0):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '3',
        'aliases': ['encode:treatment1', 'encode:treatment1']
    })
    return item


@pytest.fixture
def treatment_4(treatment_0_0, document, antibody_lot):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '4',
        'protocols': list(document),
        'antibodies': list(antibody_lot),
        'concentration': 0.25,
        'concentration_units': 'mg/mL'
    })
    return item


@pytest.fixture
def treatment_8(treatment_0_0, document):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '8',
        'treatment_type': 'protein'
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


@pytest.fixture
def treatment_9(treatment_0_0, document):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '9',
        'treatment_type': 'protein',
        'status': 'current'
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


@pytest.fixture
def treatment_10(treatment_0_0, document, lab):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '10',
        'treatment_type': 'protein',
        'status': 'in progress',
        'lab': lab['@id']
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


@pytest.fixture
def treatment_with_duration_amount_units(testapp, organism):
    item = {
        'treatment_term_name': 'ethanol',
        'treatment_type': 'chemical',
        'duration': 9,
        'duration_units': 'day',
        'amount': 100,
        'amount_units': 'mg'
    }
    return testapp.post_json('/treatment', item).json['@graph'][0]

@pytest.fixture
def treatment_11(treatment_0_0, lab):
    item = treatment_0_0.copy()
    item.update({
        'schema_version': '11',
        'treatment_type': 'stimulation',
        'status': 'in progress',
        'lab': lab['@id']
    })
    return item
