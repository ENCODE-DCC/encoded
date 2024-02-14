import pytest


def test_audit_donor_dbxref(testapp, fly_donor):
    testapp.patch_json(fly_donor['@id'], {'dbxrefs': []}),
    res = testapp.get(fly_donor['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing external identifiers' for error in errors_list)


def test_audit_donor_external_ids(testapp, fly_donor):
    testapp.patch_json(fly_donor['@id'], {'dbxrefs': [], 'external_ids': []}),
    res = testapp.get(fly_donor['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing external identifiers' for error in errors_list)


def test_audit_donor_genotype(testapp, worm_donor):
    testapp.patch_json(worm_donor['@id'], {'genotype': ''}),
    res = testapp.get(worm_donor['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genotype' for error in errors_list)
