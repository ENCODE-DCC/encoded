import pytest


@pytest.fixture
def library_protocol_base(testapp):
    item = {
        'biological_macromolecule': 'RNA',
        'library_type': 'RNA-seq',
        'name': "10x-3'-v3",
        'title': "10x 3' v3"
    }
    return testapp.post_json('/library_protocol', item, status=201).json['@graph'][0]
