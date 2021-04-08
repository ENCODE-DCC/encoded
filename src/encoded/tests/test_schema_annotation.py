import pytest


def test_annotation_with_subtype(testapp, annotation_dhs, annotation_ccre):
    testapp.patch_json(
        annotation_dhs['@id'],
        {'annotation_subtype': 'all'},
        status=422)
    testapp.patch_json(
        annotation_ccre['@id'],
        {'annotation_subtype': 'all'},
        status=200)
