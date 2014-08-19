import pytest


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }


def test_antibody_characterization_review(testapp, antibody_characterization):
    antibody_characterization['characterization_review'] = [ {"organism": "human", "lane": 2, "biosample_type": "immortalized cell line", "biosample_term_name": "K562", "biosample_term_id": "EFO:0002067"}]
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)

