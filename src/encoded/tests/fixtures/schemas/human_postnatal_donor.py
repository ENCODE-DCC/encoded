import pytest


@pytest.fixture
def human_postnatal_donor_base(testapp):
    item = {
        'sex': 'male',
        'life_stage': 'adult',
        'age': 'unknown'
    }
    return testapp.post_json('/human_postnatal_donor', item, status=201).json['@graph'][0]
