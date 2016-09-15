def test_audit_pipeline_inconsistent_assay(testapp, pipeline):
    testapp.patch_json(pipeline['@id'], {'assay_term_id': 'OBI:0001271'})
    res = testapp.get(pipeline['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent assay_term_name' for error in errors_list)
