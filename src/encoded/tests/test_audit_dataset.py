import pytest


def test_audit_publication(testapp, publication_data):
    testapp.patch_json(publication_data['@id'], {'status': 'released',
                                                 'date_released': '2016-01-01'})
    res = testapp.get(publication_data['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing reference' for error in errors_list)
