import pytest


@pytest.fixture
def reference_epigenome_1(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/reference_epigenome', item).json['@graph'][0]


@pytest.fixture
def base_reference_epigenome(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'submitted'
    }
    return testapp.post_json('/reference_epigenome', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_epigenome_16(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '16',
        'dbxrefs': ['IHEC:IHECRE00004643.1'],
    }
