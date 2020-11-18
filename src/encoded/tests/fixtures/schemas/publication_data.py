import pytest


@pytest.fixture
def publication_data_no_references(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': []
    }
    return item


@pytest.fixture
def publication_data(testapp, lab, award, publication):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': [publication['@id']],
    }
    return testapp.post_json('/publication_data', item).json['@graph'][0]
