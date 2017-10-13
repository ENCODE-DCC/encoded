import pytest


@pytest.fixture
def mouse_donor_1(testapp, award, lab, mouse):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }

@pytest.fixture
def mouse_donor_2(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]

@pytest.fixture
def mouse_donor_3(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_4(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


def test_donor_with_three_parents(
        testapp,
        mouse_donor_1,
        mouse_donor_2,
        mouse_donor_3,
        mouse_donor_4,
    ):
    mouse_donor_1['parent_strains'] = [
        mouse_donor_2,
        mouse_donor_3,
        mouse_donor_4,
    ]
    testapp.post_json('/MouseDonor', mouse_donor_1,  status=422)
