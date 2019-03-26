import pytest


@pytest.fixture
def library(lab, award):
    return {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'nucleic_acid_term_name': 'DNA'
    }


@pytest.fixture
def library_starting_quantity(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
        'nucleic_acid_starting_quantity_units': 'ng',
    })
    return item


@pytest.fixture
def library_starting_quantity_no_units(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
    })
    return item

@pytest.fixture
def library_fragmentation_method_string(library):
    item = library.copy()
    item.update(
        {
            'fragmentation_method': 'chemical (DpnII restriction)',
        }
    )
    return item

@pytest.fixture
def library_fragmentation_method_list(library):
    item = library.copy()
    item.update(
        {
            'fragmentation_method': ['chemical (DpnII restriction)', 'chemical (HindIII restriction)'],
        }
    )
    return item

def test_library_starting_quantity_post(testapp, library_starting_quantity):
    testapp.post_json('/library', library_starting_quantity)


def test_library_fragmentation_method_string(testapp, library_fragmentation_method_string):
    res = testapp.post_json('/library', library_fragmentation_method_string, expect_errors=True)
    assert res.status_code == 422

def test_library_fragmentation_method_list(testapp, library_fragmentation_method_list):
    res = testapp.post_json('/library', library_fragmentation_method_list, expect_errors=False)
    assert res.status_code == 201