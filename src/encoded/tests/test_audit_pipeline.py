import pytest


def test_audit_pipeline_assay_term_names(testapp, pipeline_without_assay_term_names):
    res = testapp.get(pipeline_without_assay_term_names['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing assay_term_names' for error in errors_list)
