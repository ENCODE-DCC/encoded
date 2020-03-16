import pytest


@pytest.fixture
def experiment_series_1(testapp, lab, award, base_experiment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'related_datasets': [base_experiment['@id']]
    }
    return testapp.post_json('/experiment_series', item, status=201).json['@graph'][0]


@pytest.fixture
def base_experiment_series(testapp, lab, award, experiment_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_1['@id']]
    }
    return testapp.post_json('/experiment-series', item, status=201).json['@graph'][0]

