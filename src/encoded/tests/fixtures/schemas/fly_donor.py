import pytest


@pytest.fixture
def fly_donor_2(testapp, award, lab, fly):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': fly['@id'],
    }
    return testapp.post_json('/fly_donor', item).json['@graph'][0]


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


@pytest.fixture
def fly_donor_3(award, lab, fly):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': fly['uuid'],
        'schema_version': '3',
        'aliases': [
            'roadmap-epigenomics:smRNA-Seq analysis of foreskin keratinocytes from skin03||Thu Jan 17 19:05:12 -0600 2013||58540||library',
            'encode:lots:of:colons*'
        ]
    }


@pytest.fixture
def fly_donor_7(root, fly, target_promoter):
    item = fly.copy()
    item.update({
        'schema_version': '7',
        'mutated_gene': target_promoter['uuid'],
        'mutagen': 'TMP/UV'
    })
    return item


@pytest.fixture
def fly_donor_9(root, fly, target_promoter):
    item = fly.copy()
    item.update({
        'schema_version': '9',
        'aliases': ['kyoto:test-alias-1'],
        'dbxrefs': ['Kyoto:123456']
    })
    return item