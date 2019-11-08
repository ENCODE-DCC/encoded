import pytest


@pytest.fixture
def publication_data_no_references(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': []
    }
    return item


def test_publication_data(testapp, publication_data_no_references, publication):
    testapp.post_json('/publication_data', publication_data_no_references, status=422)
    publication_data_no_references.update({'references': [publication['@id']]})
    testapp.post_json('/publication_data', publication_data_no_references, status=201)
