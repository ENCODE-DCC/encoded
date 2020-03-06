import pytest


@pytest.fixture
def library_data(lab, award):
    return {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'nucleic_acid_term_name': 'DNA'
    }


@pytest.fixture
def library_starting_quantity(library_data):
    item = library_data.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
        'nucleic_acid_starting_quantity_units': 'ng',
    })
    return item


@pytest.fixture
def library_starting_quantity_no_units(library_data):
    item = library_data.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
    })
    return item

@pytest.fixture
def library_with_invalid_fragmentation_methods_string(library_data):
    item = library_data.copy()
    item.update(
        {
            'fragmentation_methods': 'chemical (DpnII restriction)',
        }
    )
    return item

@pytest.fixture
def library_with_valid_fragmentation_method_list(library_data):
    item = library_data.copy()
    item.update(
        {
            'fragmentation_methods': ['chemical (DpnII restriction)', 'chemical (HindIII restriction)'],
        }
    )
    return item


def test_library_starting_quantity_post(testapp, library_starting_quantity):
    testapp.post_json('/library', library_starting_quantity)


def test_library_fragmentation_method_string(testapp, library_with_invalid_fragmentation_methods_string):
    res = testapp.post_json('/library', library_with_invalid_fragmentation_methods_string, status=422)


def test_library_fragmentation_method_list(testapp, library_with_valid_fragmentation_method_list):
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=201)