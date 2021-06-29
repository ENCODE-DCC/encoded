import pytest


def test_reference_elements_selection_method(testapp, reference):
    reference.update({'reference_type': 'index', 'elements_selection_method': ['ATAC-seq']})
    testapp.post_json('/reference', reference, status=422)
    reference.update({'reference_type': 'functional elements', 'elements_selection_method': ['ATAC-seq']})
    testapp.post_json('/reference', reference, status=201)
