import pytest


def test_audit_status_replicate(testapp, rep1):
    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched status' for error in errors_list)


def test_audit_inconsistent_modification_tag(
        testapp, rep1,
        experiment, antibody_lot, target_H3K27ac,
        target, base_biosample, construct_genetic_modification,
        library_1):
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': target_H3K27ac['@id']})
    testapp.put_json(target['@id'], {'investigated_as': ['synthetic tag'],
                                     'label': 'FLAG'})
    testapp.patch_json(rep1['@id'], {'antibody': antibody_lot['@id'],
                                     'library': library_1['@id']})
    testapp.patch_json(base_biosample['@id'], {
        'genetic_modifications': [construct_genetic_modification['@id']]})

    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent modification tag' for error in errors_list)


def test_audit_consistent_modification_tag(
        testapp, rep1,
        experiment, antibody_lot,
        target, base_biosample, construct_genetic_modification,
        library_1):
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': target['@id']})
    testapp.put_json(target['@id'], {'investigated_as': ['synthetic tag'],
                                     'label': 'FLAG'})
    testapp.patch_json(rep1['@id'], {'antibody': antibody_lot['@id'],
                                     'library': library_1['@id']})
    testapp.patch_json(construct_genetic_modification['@id'],
                       {'introduced_tags': [{'name': 'FLAG', 'location': 'C-terminal'}]})
    testapp.patch_json(base_biosample['@id'], {
        'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent modification tag' for error in errors_list)
