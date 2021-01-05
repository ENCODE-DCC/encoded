import pytest


@pytest.fixture
def mouse_postnatal_donor_base(testapp):
    item = {
        'age': '3',
        'age_units': 'year',
        'life_stage': 'premature',
        'sex': 'female',
        'strain_term_name': 'awesome strain',
    }
    return testapp.post_json('/mouse_postnatal_donor', item).json['@graph'][0]
