import pytest


@pytest.fixture
def software_version(testapp, software):
    item = {
        'version': 'v0.11.2',
        'software': software['@id'],
    }
    return testapp.post_json('/software_version', item).json['@graph'][0]

@pytest.fixture
def software_version1(testapp, software):
    item = {
        'version': 'v1.11.2',
        'software': software['@id']
    }
    return testapp.post_json('/software_version', item).json['@graph'][0]


@pytest.fixture
def software_version2(testapp, software):
    item = {
        'version': 'v1.12.2',
        'software': software['@id']
    }
    return testapp.post_json('/software_version', item).json['@graph'][0]
