import pytest


@pytest.fixture
def treatment_concentration_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_concentration_series', item, status=201).json['@graph'][0]
