import pytest


@pytest.fixture
def manatee_donor(lab, award, manatee, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': manatee['uuid'],
    }
    return testapp.post_json('/ManateeDonor', item, status=201).json['@graph'][0]
