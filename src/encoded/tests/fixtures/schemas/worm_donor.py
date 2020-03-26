import pytest


@pytest.fixture
def worm_donor(lab, award, worm, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': worm['uuid'],
        'dbxrefs': ['CGC:OP520'],
        'genotype': 'blahblahblah'
        }
    return testapp.post_json('/WormDonor', item, status=201).json['@graph'][0]
