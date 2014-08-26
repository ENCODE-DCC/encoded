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


def test_audit_antibody_mismatched_in_review(testapp, base_antibody_characterization, base_characterization_review):
    testapp.patch_json(base_antibody_characterization['@id'], {'primary_characterization_method': 'immunoblot'})
    base_characterization_review['biosample_term_name'] = 'qwijibo'
    characterization_review_list = []
    characterization_review_list.append(base_characterization_review)
    testapp.patch_json(base_antibody_characterization['@id'], {'characterization_reviews': characterization_review_list})
    res = testapp.get(base_antibody_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'term id not in ontology' for error in errors)
