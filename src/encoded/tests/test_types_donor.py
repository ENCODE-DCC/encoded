import pytest


@pytest.fixture
def parent(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def child(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


# patch parent to child, check that children are a calculated property for the parent
def test_types_calculated_children(testapp, parent, child):
    testapp.patch_json(child['@id'],
                             {'parents': [parent['@id']]}).json['@graph'][0]
    res = testapp.get(parent['@id'] + '@@index-data')
    assert res.json['object']['children'] == [child['@id']]
