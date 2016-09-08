def test_audit_pipeline_assay_term_id(testapp, pipeline):
    res = testapp.get(pipeline['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'missing assay information' for error in errors_list)


def test_audit_pipeline_assay_term_name(testapp, pipeline):
    testapp.patch_json(pipeline['@id'], {'assay_term_id': 'NTR:0003082'})
    res = testapp.get(pipeline['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'missing assay information' for error in errors_list)


def test_audit_pipeline_assay_term_name_mixed(testapp, pipeline):
    testapp.patch_json(pipeline['@id'], {'assay_term_id': 'NTR:0003082',
                                         'assay_term_name': 'RNA-seq'})
    res = testapp.get(pipeline['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent assay_term_name' for error in errors_list)
