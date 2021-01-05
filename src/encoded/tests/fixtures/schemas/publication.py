import pytest


@pytest.fixture
def publication_base(testapp):
    item = {
        # upgrade/shared.py has a REFERENCES_UUID mapping.
        'uuid': '8312fc0c-b241-4cb2-9b01-1438910550ad',
        'title': "Test publication",
        'abstract': 'Super duper interesting text.',
    }
    print('submit publication')
    return testapp.post_json('/publication', item).json['@graph'][0]
