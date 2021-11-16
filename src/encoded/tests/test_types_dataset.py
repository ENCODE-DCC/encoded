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


def test_transgenic_enhancer_experiment_datapoint(testapp, transgenic_enhancer_experiment):
    # https://encodedcc.atlassian.net/browse/ENCD-6195
    res = testapp.get(transgenic_enhancer_experiment['@id'] + '@@index-data')
    assert res.json['object']['datapoint'] is False


def test_fcc_series_titles(testapp, base_functional_characterization_series, pooled_clone_sequencing, fcc_posted_CRISPR_screen):
    # https://encodedcc.atlassian.net/browse/ENCD-6232
    testapp.patch_json(base_functional_characterization_series['@id'], 
        {'related_datasets': [
            fcc_posted_CRISPR_screen['@id'],
            pooled_clone_sequencing['@id'],
            ]
        }
    )
    res = testapp.get(base_functional_characterization_series['@id'] + '@@index-data') 
    assert res.json['object']['assay_title'] == [fcc_posted_CRISPR_screen.get('assay_title')]