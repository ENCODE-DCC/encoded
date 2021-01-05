import pytest


@pytest.fixture
def document_base(testapp):
    item = {
        'document_type': 'growth protocol'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]
