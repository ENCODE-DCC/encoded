import pytest


@pytest.fixture
def parent_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def child_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


def test_types_calculated_children(testapp, parent_human_donor, child_human_donor):
    testapp.patch_json(child_human_donor['@id'],
                             {'parents': [parent_human_donor['@id']]}).json['@graph'][0]
    res = testapp.get(parent_human_donor['@id'] + '@@index-data')
    assert res.json['object']['children'] == [child_human_donor['@id']]
