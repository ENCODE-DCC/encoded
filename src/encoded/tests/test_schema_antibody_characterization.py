import pytest


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }


def test_antiboddy_characterization_two_methods(testapp, antibody_characterization):
    antibody_characterization['primary_characterization_method'] = 'immunoblot'
    antibody_characterization['secondary_characterization_method'] = 'ChIP-seq comparison'
    testapp.post_json('/antibody_characterization', antibody_characterization,  status=422)