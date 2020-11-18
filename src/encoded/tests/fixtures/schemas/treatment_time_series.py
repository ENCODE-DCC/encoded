import pytest


@pytest.fixture
def treatment_time_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_time_series', item, status=201).json['@graph'][0]
