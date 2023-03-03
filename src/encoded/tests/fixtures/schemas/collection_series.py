import pytest


@pytest.fixture
def base_collection_series(testapp, lab, base_fcc_experiment, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_fcc_experiment['@id']]
    }
    return testapp.post_json('/collection_series', item, status=201).json['@graph'][0]


@pytest.fixture
def collection_series_1(testapp, lab, base_fcc_experiment, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_fcc_experiment['@id']],
        'schema_version': '1',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
