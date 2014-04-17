import pytest


@pytest.fixture
def library(experiment):
    return {
        'lab': experiment['lab']['uuid'],
        'award': experiment['award']['uuid'],
        'nucleic_acid_term_name': "DNA",
        'nucleic_acid_term_id': "SO:0000352"
    }


@pytest.fixture
def library_starting_quantity(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': 10,
        'nucleic_acid_starting_quantity_units': "ng",
    })
    return item


@pytest.fixture
def library_starting_quantity_no_units(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': 10,
    })
    return item


def test_library_starting_quantity_post(testapp, library_starting_quantity):
    testapp.post_json('/library', library_starting_quantity)


def test_library_starting_unit_requirement(testapp, library_starting_quantity_no_units):
   testapp.post_json('/replicate', library_starting_quantity_no_units, status=422)