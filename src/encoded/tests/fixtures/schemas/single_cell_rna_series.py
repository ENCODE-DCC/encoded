import pytest


@pytest.fixture
def base_single_cell_series(testapp, lab, base_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment_submitted['@id']]
    }
    return testapp.post_json('/single_cell_rna_series', item, status=201).json['@graph'][0]


@pytest.fixture
def single_cell_series(testapp, lab, base_single_cell_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_single_cell_experiment_submitted['@id']]
    }
    return testapp.post_json('/single_cell_rna_series', item, status=201).json['@graph'][0]


@pytest.fixture
def single_cell_series_3(testapp, lab, base_single_cell_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_single_cell_experiment_submitted['@id']],
        'schema_version': '3',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
