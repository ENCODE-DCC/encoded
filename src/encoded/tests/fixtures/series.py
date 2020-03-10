import pytest
from ..constants import *


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


@pytest.fixture
def base_single_cell_series(testapp, lab, base_experiment, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment['@id']]
    }
    return testapp.post_json('/single_cell_rna_series', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_time_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_time_series', item, status=201).json['@graph'][0]

