import pytest


def test_audit_pipeline_assay_term_names(testapp, treatment_12):
    res = testapp.get(treatment_12['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing treatment purpose' for error in errors_list)
