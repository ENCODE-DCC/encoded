import pytest


@pytest.fixture
def human_postnatal_donor_base(testapp, adult_ontology, european_ontology):
    item = {
        'sex': 'male',
        'development_ontology': adult_ontology['@id'],
        'age': 'unknown',
        'ethnicity': european_ontology['@id']
    }
    return testapp.post_json('/human_postnatal_donor', item, status=201).json['@graph'][0]
