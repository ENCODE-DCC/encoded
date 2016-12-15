def test_audit_pipeline_assay_term_id(testapp, pipeline):
    res = testapp.get(pipeline['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'missing assay information' for error in errors_list)
