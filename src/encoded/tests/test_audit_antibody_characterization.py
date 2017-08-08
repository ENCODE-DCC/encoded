import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


@pytest.fixture
def base_antibody_characterization(testapp, lab, ENCODE3_award, target, antibody_lot, organism):
    characterization_review_list = [{
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'lane_status': 'pending dcc review'
    }]
    item = {
        'award': ENCODE3_award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'primary_characterization_method': 'immunoblot',
        'characterization_reviews': characterization_review_list,
        'status': 'pending dcc review'
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
        'project': 'ENCODE'
    }
    return testapp.post_json('/award', item, status=201).json['@graph'][0]


def test_audit_antibody_mismatched_in_review(testapp, base_antibody_characterization):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list[0]['biosample_term_name'] = 'qwijibo'
    testapp.patch_json(base_antibody_characterization['@id'],
                       {'characterization_reviews': characterization_review_list})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent ontology term' for error in errors_list)


def test_audit_antibody_biosample_ntr_term_in_review(testapp, base_antibody_characterization):
    characterization_review_list = base_antibody_characterization.get('characterization_reviews')
    characterization_review_list[0]['biosample_term_id'] = 'NTR:0001264'
    characterization_review_list[0]['biosample_term_name'] = 'pancreas'
    testapp.patch_json(base_antibody_characterization['@id'],
                       {'characterization_reviews': characterization_review_list})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'characterization review with invalid biosample term id' for error in errors_list)


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
