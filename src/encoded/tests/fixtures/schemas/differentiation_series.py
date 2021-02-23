import pytest


@pytest.fixture
def base_differentiation_series(testapp, lab, base_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment_submitted['@id']]
    }
    return testapp.post_json('/differentiation_series', item, status=201).json['@graph'][0]
