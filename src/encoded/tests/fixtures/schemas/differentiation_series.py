import pytest


@pytest.fixture
def base_differentiation_series(testapp, lab, base_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment_submitted['@id']]
    }
    return testapp.post_json('/differentiation_series', item, status=201).json['@graph'][0]


@pytest.fixture
def treated_differentiation_series(testapp, lab, award, experiment_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_1['@id']]
    }
    return testapp.post_json('/differentiation_series', item, status=201).json['@graph'][0]


@pytest.fixture
def differentiation_series_1(testapp, lab, base_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment_submitted['@id']],
        'schema_version': '1',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
