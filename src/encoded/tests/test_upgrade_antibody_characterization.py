import pytest


@pytest.fixture
def antibody_characterization_0(submitter, lab, award, antibody, target, attachment):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody['uuid'],
        'target': target['uuid'],
        'attachment': attachment['uuid']
    }


@pytest.fixture
def antibody_characterization_11(antibody_characterization_0):
    item = antibody_characterization_0.copy()
    item.update({
        'characterization_reviews': [
        {
            'biosample_term_name': 'K562',
            'biosample_term_id': 'EFO:0002067',
            'lane_status': 'exempt from standards',
            'biosample_type': 'immortalized cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }
    ]
    })
    return item


def test_upgrade_antibody_characterization_11_to_12(upgrader, antibody_characterization_11, biosample):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_11, current_version='11', target_version='12')
    assert value['characterization_reviews']['biosample_type'] == 'cell line'
