import pytest


@pytest.fixture
def treatment_concentration_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_concentration_series', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_concentration_series_17(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'schema_version': '17',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item