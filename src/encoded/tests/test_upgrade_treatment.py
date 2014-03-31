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


def test_treatment_upgrade(app, treatment_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:Estradiol_1nM']
    assert 'award' not in value  

def test_treatment_upgrade_encode_dbxref(app, treatment_1):
    treatment_1['encode2_dbxrefs'] = ["encode:hESC to endoderm differentiation treatment"]
    migrator = app.registry['migrator']
    value = migrator.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:hESC to endoderm differentiation treatment']
    assert 'award' not in value  