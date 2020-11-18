import pytest


@pytest.fixture
def base_analysis(testapp, file1):
    item = {
        'files': [file1['@id']],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]
