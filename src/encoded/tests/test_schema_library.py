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


def test_library_starting_quantity_post(testapp, library_starting_quantity):
    testapp.post_json('/library', library_starting_quantity)
