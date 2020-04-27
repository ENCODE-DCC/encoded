import pytest


@pytest.fixture
def base_reference(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/reference', item).json['@graph'][0]
