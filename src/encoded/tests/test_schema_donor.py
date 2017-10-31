import pytest


@pytest.fixture
def mouse_donor_to_test(testapp, lab, award, mouse):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }


def test_donor_with_no_parents(testapp, mouse_donor_to_test):
    mouse_donor_to_test['parent_strains'] = []
    testapp.post_json('/mouse_donor', mouse_donor_to_test, status=422)


def test_donor_with_three_parents(
        testapp,
        mouse_donor_to_test,
        mouse_donor,
        mouse_donor_1,
        mouse_donor_2):
    mouse_donor_to_test['parent_strains'] = [
        mouse_donor['@id'],
        mouse_donor_1['@id'],
        mouse_donor_2['@id'],
    ]
    testapp.post_json('/mouse_donor', mouse_donor_to_test, status=422)
