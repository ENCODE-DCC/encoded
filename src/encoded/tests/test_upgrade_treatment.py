import pytest


@pytest.fixture
def treatment():
    return{
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'	
    }

@pytest.fixture
def treatment_1(treatment):
    item = treatment.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['Estradiol_1nM'],
    })
    return item


def test_treatment_upgrade(app, treatment_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['ucsc_encode_db:Estradiol_1nM']
