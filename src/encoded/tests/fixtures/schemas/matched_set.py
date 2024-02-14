import pytest


@pytest.fixture
def matched_set(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id']
    }
    return item


@pytest.fixture
def base_matched_set(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/matched_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matched_set_17(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'schema_version': '17',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
