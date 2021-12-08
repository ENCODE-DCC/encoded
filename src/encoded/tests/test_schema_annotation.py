import pytest


def test_annotation_with_subtype(
    testapp,
    submitter_testapp,
    annotation_dhs,
    annotation_ccre_2,
    annotation_dataset
):
    testapp.patch_json(
        annotation_dhs['@id'],
        {'annotation_subtype': 'all'},
        status=200)
    # annotation_subtype can only be submitted with admin permissions
    res = testapp.post_json('/annotation', annotation_ccre_2, status=201)
    submitter_testapp.patch_json(
        res.json['@graph'][0]['@id'],
        {'annotation_subtype': 'all'}, status=422)
    testapp.patch_json(
        res.json['@graph'][0]['@id'],
        {'annotation_subtype': 'all'}, status=200)
    # annotation_subtype may be submitted for cCRE or rDHS only
    testapp.patch_json(
        annotation_dataset['@id'],
        {'annotation_subtype': 'all'},
        status=422)

def test_annotation_fine_mapped(
    testapp,
    submitter_testapp,
    annotation_fine_mapped
):
    res = testapp.post_json('/annotation', annotation_fine_mapped, status=201)
    submitter_testapp.patch_json(
        res.json['@graph'][0]['@id'],
        {'annotation_type': 'other'}, status=422)
