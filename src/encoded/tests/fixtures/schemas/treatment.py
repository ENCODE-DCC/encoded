import pytest


@pytest.fixture
def treatment_base(testapp):
    item = {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }
    return testapp.post_json('/treatment', item).json['@graph'][0]
