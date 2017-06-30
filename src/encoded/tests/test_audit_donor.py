import pytest


@pytest.fixture
def worm(testapp):
    item = {
        'uuid': '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20',
        'name': 'celegans',
        'scientific_name': 'Caenorhabditis elegans',
        'taxon_id': '6239',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


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


@pytest.fixture
def fly_donor(lab, award, fly, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': fly['uuid'],
        'dbxrefs': ['FlyBase:FBst0000003'],
        'genotype': 'blahblah'
        }
    return testapp.post_json('/FlyDonor', item, status=201).json['@graph'][0]


def test_audit_donor_dbxref(testapp, fly_donor):
    testapp.patch_json(fly_donor['@id'], {'dbxrefs': []}),
    res = testapp.get(fly_donor['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing dbxrefs' for error in errors_list)


def test_audit_donor_genotype(testapp, worm_donor):
    testapp.patch_json(worm_donor['@id'], {'genotype': ''}),
    res = testapp.get(worm_donor['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genotype' for error in errors_list)
