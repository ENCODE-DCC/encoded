import pytest


def test_donor_with_no_parents(testapp, mouse_donor_to_test):
    mouse_donor_to_test['parent_strains'] = []
    testapp.post_json('/mouse_donor', mouse_donor_to_test, status=422)


def test_donor_with_three_parents(
        testapp,
        mouse_donor_to_test,
        mouse_donor,
        mouse_donor_1_1,
        mouse_donor_2_1):
    mouse_donor_to_test['parent_strains'] = [
        mouse_donor['@id'],
        mouse_donor_1_1['@id'],
        mouse_donor_2_1['@id'],
    ]
    testapp.post_json('/mouse_donor', mouse_donor_to_test, status=422)
