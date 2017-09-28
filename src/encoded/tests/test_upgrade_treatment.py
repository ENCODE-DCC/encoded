import pytest


@pytest.fixture
def treatment():
    return{
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }


@pytest.fixture
def treatment_1(treatment, award):
    item = treatment.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['Estradiol_1nM'],
        'award': award['uuid'],
    })
    return item


@pytest.fixture
def treatment_2(treatment):
    item = treatment.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def treatment_3(treatment):
    item = treatment.copy()
    item.update({
        'schema_version': '3',
        'aliases': ['encode:treatment1', 'encode:treatment1']
    })
    return item


@pytest.fixture
def treatment_4(treatment, document, antibody_lot):
    item = treatment.copy()
    item.update({
        'schema_version': '4',
        'protocols': list(document),
        'antibodies': list(antibody_lot),
        'concentration': 0.25,
        'concentration_units': 'mg/mL'
    })
    return item


@pytest.fixture
def treatment_8(treatment, document):
    item = treatment.copy()
    item.update({
        'schema_version': '8',
        'treatment_type': 'protein'
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


def test_treatment_upgrade(upgrader, treatment_1):
    value = upgrader.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:Estradiol_1nM']
    assert 'award' not in value


def test_treatment_upgrade_encode_dbxref(upgrader, treatment_1):
    treatment_1['encode2_dbxrefs'] = ["encode:hESC to endoderm differentiation treatment"]
    value = upgrader.upgrade('treatment', treatment_1, current_version = '1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:hESC to endoderm differentiation treatment']
    assert 'award' not in value


def test_treatment_upgrade_status(upgrader, treatment_2):
    value = upgrader.upgrade('treatment', treatment_2, current_version = '2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'


def test_treatment_upgrade_3_4(upgrader, treatment_3):
    value = upgrader.upgrade('treatment', treatment_3, current_version = '3', target_version='4')
    assert value['schema_version'] == '4'
    assert len(value['aliases']) == 1


def test_treatment_upgrade_4_to_5(upgrader, treatment_4):
    value = upgrader.upgrade('treatment', treatment_4, current_version = '4', target_version='5')
    assert value['schema_version'] == '5'
    assert 'protocols' not in value
    assert 'documents' in value
    assert 'antibodies' not in value
    assert 'antibodies_used' in value
    assert 'concentation' not in value
    assert 'amount' in value
    assert 'concentation_units' not in value
    assert 'amount_units' in value


def test_treatment_upgrade_8_to_9(upgrader, treatment_8):
    value = upgrader.upgrade('treatment', treatment_8, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert value['treatment_term_id'] == 'UniProtKB:P03823'
