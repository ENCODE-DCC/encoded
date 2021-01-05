import pytest


@pytest.fixture
def heart_ontology(testapp):
    item = {
        'term_id': 'UBERON:0000948',
        'term_name': 'heart',
    }
    return testapp.post_json('/ontology_term', item).json['@graph'][0]
