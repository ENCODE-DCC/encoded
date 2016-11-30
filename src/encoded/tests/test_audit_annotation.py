import pytest


def test_audit_annotation_missing_organism(testapp, annotation_dataset):
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing organism' for error in errors_list)
