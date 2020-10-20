import pytest


def test_genetic_modification_reagents(testapp, genetic_modification, source):
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        if error_type == 'WARNING':
            errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genetic modification reagents' for
               error in errors_list)
    testapp.patch_json(genetic_modification['@id'], {'reagents': [
        {
            'source': source['@id'],
            'identifier': 'trc:TRCN0000246247'
        }]})
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing genetic modification reagents' for
        error in errors_list)


def test_audit_reagent_source(testapp, source, genetic_modification_source):
    testapp.patch_json(
        genetic_modification_source['@id'],
        {
            'reagents': [
                {
                    'source': source['@id'],
                    'identifier': 'trc:TRCN1234567890'
                }
            ]
        }
    )
    res = testapp.get(genetic_modification_source['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent genetic modification reagent source and identifier' for error in errors_list)


def test_genetic_modification_reagents_fly(testapp, genetic_modification_RNAi, fly_donor):
    res = testapp.get(genetic_modification_RNAi['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genetic modification reagents' for
               error in errors_list)
    testapp.patch_json(fly_donor['@id'], {'genetic_modifications': [genetic_modification_RNAi['@id']]})
    res = testapp.get(genetic_modification_RNAi['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing genetic modification reagents' for
               error in errors_list)


def test_genetic_modification_target(testapp, construct_genetic_modification,
                                     tagged_target):
    testapp.patch_json(construct_genetic_modification['@id'],
                       {'modified_site_by_target_id': tagged_target['@id']})
    res = testapp.get(construct_genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent modification target' for
               error in errors_list)
