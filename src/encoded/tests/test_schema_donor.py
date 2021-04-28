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


def test_donor_manatee_incomplete_age(testapp, manatee_donor):
    # https://encodedcc.atlassian.net/browse/ENCD-5892
    testapp.patch_json(manatee_donor['@id'], {'age': '12'}, status=422)
    testapp.patch_json(manatee_donor['@id'], {'age_units': 'year'}, status=422)
    testapp.patch_json(manatee_donor['@id'], {'age': 'unknown'}, status=200)
    testapp.patch_json(manatee_donor['@id'], {'age': '12', 'age_units': 'year'}, status=200)
