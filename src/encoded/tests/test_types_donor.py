import pytest


def test_types_calculated_children(testapp, parent_human_donor, child_human_donor):
    testapp.patch_json(child_human_donor['@id'],
                             {'parents': [parent_human_donor['@id']]}).json['@graph'][0]
    res = testapp.get(parent_human_donor['@id'] + '@@index-data')
    assert res.json['object']['children'] == [child_human_donor['@id']]


def test_types_calculated_superseded(testapp, parent_human_donor, child_human_donor):
    testapp.patch_json(child_human_donor['@id'],
                             {'supersedes': [parent_human_donor['@id']]}).json['@graph'][0]
    res = testapp.get(parent_human_donor['@id'] + '@@index-data')
    assert res.json['object']['superseded_by'] == [child_human_donor['@id']]
