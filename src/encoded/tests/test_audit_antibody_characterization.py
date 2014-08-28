import pytest


@pytest.fixture
def base_antibody_characterization(testapp, lab, award, target, antibody_lot):
    item = {
        'award': award['uuid'],
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
def base_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'growth protocol'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


def test_audit_antibody_mismatched_in_review(testapp, base_antibody_characterization, base_characterization_review):
    base_characterization_review['biosample_term_name'] = 'qwijibo'
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot'})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'term id not in ontology' for error in errors)


def test_audit_antibody_no_standards(testapp, base_antibody_characterization, base_characterization_review, base_document, wrangler):
    characterization_review_list = []
    base_characterization_review['lane_status'] = 'compliant'
    characterization_review_list.append(base_characterization_review)
    reviewed_by = "/users/" + wrangler['uuid'] + "/"
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot', 'status': 'compliant', 'documents': [base_document['uuid']], 'reviewed_by': reviewed_by  })
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing standards' for error in errors)

def test_audit_antibody_duplicate_review_subobject(testapp, base_antibody_characterization, base_characterization_review, base_document):
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list, 'primary_characterization_method': 'immunoblot' })
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'duplicate lane review' for error in errors)