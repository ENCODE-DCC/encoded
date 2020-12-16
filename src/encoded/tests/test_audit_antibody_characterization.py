import pytest


def test_audit_antibody_mismatched_in_review(testapp,
                                             base_antibody_characterization,
                                             inconsistent_biosample_type):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list[0]['biosample_ontology'] = inconsistent_biosample_type['uuid']
    testapp.patch_json(base_antibody_characterization['@id'],
                       {'characterization_reviews': characterization_review_list})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent ontology term' for error in errors_list)


def test_audit_antibody_duplicate_review_subobject(testapp, base_antibody_characterization, base_characterization_review, base_document):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'duplicate lane review' for error in errors_list)


def test_audit_antibody_target_mismatch(testapp, base_antibody_characterization, base_target):
    testapp.patch_json(base_antibody_characterization['@id'], {'target': base_target['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent target' for error in errors_list)


def test_audit_antibody_not_tag_antibody(testapp, base_antibody_characterization, recombinant_target):
    testapp.patch_json(base_antibody_characterization['@id'], {'target': recombinant_target['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not tagged antibody' for error in errors_list)


def test_audit_antibody_target_tag_antibody(testapp, base_antibody_characterization, base_antibody, recombinant_target, tag_target):
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_antibody_characterization['@id'], {'target': recombinant_target['@id'], 'characterizes': tag_antibody['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched tag target' for error in errors_list)


def test_audit_antibody_lane_status_pending_mismatch1(testapp, base_antibody_characterization, base_antibody, wrangler, standards_document):
    reviewed_by = "/users/" + wrangler['uuid'] + "/"
    testapp.patch_json(base_antibody_characterization['@id'], {'status': 'compliant', 'reviewed_by': reviewed_by, 'documents': [standards_document['uuid']]})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched lane status' for error in errors_list)


def test_audit_antibody_lane_status_pending_mismatch2(testapp, base_antibody_characterization, base_antibody, ):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list[0]['lane_status'] = 'compliant'
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'status': 'pending dcc review'})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched lane status' for error in errors_list)


def test_audit_antibody_lane_status_compliant_mismatch(testapp, base_antibody_characterization, base_antibody, base_characterization_review2, wrangler, standards_document):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list[0]['lane_status'] = 'not compliant'
    characterization_review_list.append(base_characterization_review2)
    reviewed_by = "/users/" + wrangler['uuid'] + "/"
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'status': 'not compliant', 'reviewed_by': reviewed_by, 'documents': [standards_document['uuid']]})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched lane status' for error in errors_list)
