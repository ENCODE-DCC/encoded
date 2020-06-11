import pytest


def test_library_starting_quantity_post(testapp, library_starting_quantity):
    testapp.post_json('/library', library_starting_quantity)


def test_library_fragmentation_method_string(testapp, library_with_invalid_fragmentation_methods_string):
    res = testapp.post_json('/library', library_with_invalid_fragmentation_methods_string, status=422)


def test_library_fragmentation_method_list(testapp, library_with_valid_fragmentation_method_list):
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=201)


def test_library_fragmentation_method_list(testapp, library_with_valid_fragmentation_method_list):
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=201)
    library_with_valid_fragmentation_method_list.update({'fragmentation_duration_time': 5})
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=422)
    library_with_valid_fragmentation_method_list.update({'fragmentation_duration_time_units': 'minutes'})
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=201)
    library_with_valid_fragmentation_method_list.pop('fragmentation_methods')
    testapp.post_json('/library', library_with_valid_fragmentation_method_list, status=422)


def test_library_size_SD_and_CV_properties(testapp, library_size_range, library_fragment_length_CV):
    # https://encodedcc.atlassian.net/browse/ENCD-5276
    testapp.post_json('/library', library_size_range, status=201)
    library_size_range.update({'average_fragment_size': 350})
    testapp.post_json('/library', library_size_range, status=422)
    library_size_range.pop('size_range')
    testapp.post_json('/library', library_size_range, status=201)

    testapp.post_json('/library', library_fragment_length_CV, status=201)
    library_fragment_length_CV.update({'fragment_length_SD': 45})
    testapp.post_json('/library', library_fragment_length_CV, status=422)
    library_fragment_length_CV.pop('fragment_length_CV')
    testapp.post_json('/library', library_fragment_length_CV, status=201)


def test_library_adapters(testapp, library, file):
    file_adapters = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
            },
        ]
    }
    testapp.post_json('/library', file_adapters, status=201)
    sequence_adapters = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'sequence': 'GGGGGGCNA',
            },
            {
                'type': "read1 3' adapter",
                'sequence': 'GGGGGGCNAT',
            },
        ]
    }
    testapp.post_json('/library', sequence_adapters, status=201)
    file_sequence_adapter1 = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
                'sequence': 'GGGGGGCNA',
            },
        ]
    }
    testapp.post_json('/library', file_sequence_adapter1, status=422)
    file_sequence_adapter2 = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
            },
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
                'sequence': 'GGGGGGCNA',
            },
        ]
    }
    testapp.post_json('/library', file_sequence_adapter2, status=422)
    mixed_adapters = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
            },
            {
                'type': "read1 3' adapter",
                'sequence': 'GGGGGGCNA',
            },
        ]
    }
    testapp.post_json('/library', mixed_adapters, status=422)


def test_library_adapters_type(testapp, library, file):
    adapters = {
        **library,
        'adapters': [
            {
                'type': "read1 3' adapter",
                'file': file['@id'],
            },
        ]
    }
    testapp.post_json('/library', adapters, status=201)
    adapters_missing_type = {
        **library,
        'adapters': [
            {
                'sequence': 'GGGGGGCNA',
            }
        ]
    }
    testapp.post_json('/library', adapters_missing_type, status=422)
