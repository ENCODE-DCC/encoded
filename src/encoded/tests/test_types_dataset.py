import pytest


def test_annotation_biochemical_inputs(testapp, file_ccre,
                                       annotation_ccre,
                                       file_ccre_2, file_ccre_3):
    # https://encodedcc.atlassian.net/browse/ENCD-5717
    testapp.patch_json(file_ccre['@id'], {'derived_from': [file_ccre_2['@id'], file_ccre_3['@id']]})
    res = testapp.get(annotation_ccre['@id'] + '@@index-data')
    assert res.json['object']['biochemical_inputs'] == ['cDHS', 'rDHS']


def test_fcc_datapoint(testapp, base_functional_characterization_series):
    # https://encodedcc.atlassian.net/browse/ENCD-6148
    res = testapp.get(base_functional_characterization_series['@id'] + '@@index-data') 
    assert res.json['object']['datapoint'] is False
