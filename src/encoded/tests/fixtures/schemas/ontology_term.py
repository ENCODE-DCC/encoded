import pytest


@pytest.fixture
def heart_ontology(testapp):
    item = {
        'term_id': 'UBERON:0003498',
        'term_name': 'heart blood vessel',
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]
