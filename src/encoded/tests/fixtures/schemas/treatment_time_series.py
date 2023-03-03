import pytest


@pytest.fixture
def treatment_time_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_time_series', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_time_series_18(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'schema_version': '18',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item