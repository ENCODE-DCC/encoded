import pytest


@pytest.fixture
def base_antibody_characterization(testapp, lab, ENCODE3_award, target, antibody_lot):
    item = {
        'award': ENCODE3_award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid']
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_characterization_review(testapp, organism):
    return {
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'lane_status': 'pending dcc review'
    }


@pytest.fixture
def base_characterization_review2(testapp, organism):
    return {
        'lane': 3,
        'organism': organism['uuid'],
        'biosample_term_name': 'HepG2',
        'biosample_term_id': 'EFO:0001187',
        'biosample_type': 'immortalized cell line',
        'lane_status': 'compliant'
    }

@pytest.fixture
def base_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'growth protocol'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


@pytest.fixture
def standards_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'standards document'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'TAF1',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody(award, lab, source, organism, target):
   return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [target['uuid']],
        'product_id': 'KDKF123',
        'lot_id': '123'
    }


@pytest.fixture
def recombinant_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'HA-ABCD',
        'investigated_as': ['transcription factor', 'recombinant protein'],
        'gene_name': "ABCD"
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def ENCODE3_award(testapp):
    item = {
        'name': 'ABC1234',
        'rfa': 'ENCODE3',
    }
    return testapp.post_json('/award', item, status=201).json['@graph'][0]


def test_audit_antibody_mismatched_in_review(testapp, base_antibody_characterization, base_characterization_review):
    base_characterization_review['biosample_term_name'] = 'qwijibo'
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'status': 'pending dcc review'})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'term name mismatch' for error in errors_list)


def test_audit_antibody_duplicate_review_subobject(testapp, base_antibody_characterization, base_characterization_review, base_document):
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'status': 'pending dcc review' })
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'duplicate lane review' for error in errors_list)


def test_audit_antibody_target_mismatch(testapp, base_antibody_characterization, base_target, base_characterization_review, antibody_lot):
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': base_target['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'target mismatch' for error in errors_list)


def test_audit_antibody_not_tag_antibody(testapp, base_antibody_characterization, recombinant_target, base_characterization_review,):
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': recombinant_target['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not tagged antibody' for error in errors_list)


def test_audit_antibody_target_tag_antibody(testapp, base_antibody_characterization, base_antibody, recombinant_target, base_characterization_review, tag_target):
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': recombinant_target['@id'], 'characterizes': tag_antibody['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'tag target mismatch' for error in errors_list)


def test_audit_antibody_lane_status_pending_mismatch1(testapp, base_antibody_characterization, base_antibody, target, base_characterization_review, wrangler, standards_document):
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    reviewed_by = "/users/" + wrangler['uuid'] + "/"
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': target['@id'], 'status': 'compliant', 'reviewed_by': reviewed_by, 'documents': [standards_document['uuid']]})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'lane status mismatch' for error in errors_list)


def test_audit_antibody_lane_status_pending_mismatch2(testapp, base_antibody_characterization, base_antibody, target, base_characterization_review):
    characterization_review_list = []
    base_characterization_review['lane_status'] = 'compliant'
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': target['@id'], 'status': 'pending dcc review'})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'lane status mismatch' for error in errors_list)


def test_audit_antibody_lane_status_compliant_mismatch(testapp, base_antibody_characterization, base_antibody, target, base_characterization_review, base_characterization_review2, wrangler, standards_document):
    characterization_review_list = []
    base_characterization_review['lane_status'] = 'not compliant'
    characterization_review_list.append(base_characterization_review)
    characterization_review_list.append(base_characterization_review2)
    reviewed_by = "/users/" + wrangler['uuid'] + "/"
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'target': target['@id'], 'status': 'not compliant', 'reviewed_by': reviewed_by, 'documents': [standards_document['uuid']]})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'lane status mismatch' for error in errors_list)


def test_audit_unapproved_antibody_characterization_method1(testapp, base_antibody_characterization):
    testapp.patch_json(base_antibody_characterization['@id'], {'secondary_characterization_method': 'motif enrichment'})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unapproved char method' for error in errors_list)


def test_audit_unapproved_antibody_characterization_method2(testapp, base_antibody_characterization, target):
    testapp.patch_json(target['@id'], {'investigated_as': ['histone modification']})
    testapp.patch_json(base_antibody_characterization['@id'], {'secondary_characterization_method': 'ChIP-seq comparison', 'target': target['@id']})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unapproved char method' for error in errors_list)
