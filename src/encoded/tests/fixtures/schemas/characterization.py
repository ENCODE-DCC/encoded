import pytest


@pytest.fixture
def base_characterization_review(testapp, organism, k562):
    return {
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_ontology': k562['uuid'],
        'lane_status': 'pending dcc review'
    }


@pytest.fixture
def base_characterization_review2(testapp, organism, hepg2):
    return {
        'lane': 3,
        'organism': organism['uuid'],
        'biosample_ontology': hepg2['uuid'],
        'lane_status': 'compliant'
    }

@pytest.fixture
def review(lab, submitter):
    review = {
        'reviewed_by': submitter['@id'],
        'status': 'compliant',
        'lab': lab['@id'],
    }
    return review
