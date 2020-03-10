import pytest
from ..constants import *


@pytest.fixture
def fly_donor(testapp, award, lab, fly):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': fly['@id'],
    }
    return testapp.post_json('/fly_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_1(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_2(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_to_test(testapp, lab, award, mouse):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }

@pytest.fixture
def human_donor(testapp, award, lab, human):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': human['@id'],
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def human_donor_2(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']        
    }

@pytest.fixture
def parent_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def child_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]

@pytest.fixture
def human_donor_upgrade(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
    }


@pytest.fixture
def mouse_donor_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': '3413218c-3d86-498b-a0a2-9a406638e786',
    }


@pytest.fixture
def human_donor_1(human_donor_upgrade):
    item = human_donor_upgrade.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def human_donor_2(human_donor_upgrade):
    item = human_donor_upgrade.copy()
    item.update({
        'schema_version': '2',
        'age': '11.0'
    })
    return item


@pytest.fixture
def mouse_donor_1(mouse_donor_base):
    item = mouse_donor_base.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def mouse_donor_2(mouse_donor_base):
    item = mouse_donor_base.copy()
    item.update({
        'schema_version': '2',
        'sex': 'male',

    })
    return item


@pytest.fixture
def mouse_donor_3(root, mouse_donor, publication):
    item = root.get_by_uuid(mouse_donor['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'references': [publication['identifiers'][0]],

    })
    return properties


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
def human_donor_6(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '6',
        'aliases': [
            'encode:why||put||up||bars',
            'encode:lots:and:lots:of:colons!'
        ]
    })
    return properties


@pytest.fixture
def human_donor_9(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '9',
        'life_stage': 'postnatal',
        'ethnicity': 'caucasian'
    })
    return properties


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
def human_donor_10(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'genetic_modifications': []
    })
    return properties


@pytest.fixture
def mouse_donor_10(root, mouse_donor):
    item = root.get_by_uuid(mouse_donor['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'parent_strains': []
    })
    return properties

@pytest.fixture
def fly_donor_9(root, fly, target_promoter):
    item = fly.copy()
    item.update({
        'schema_version': '9',
        'aliases': ['kyoto:test-alias-1'],
        'dbxrefs': ['Kyoto:123456']
    })
    return item

@pytest.fixture
def base_human_donor(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]

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
def fly_donor_201(lab, award, fly, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': fly['uuid'],
        'dbxrefs': ['FlyBase:FBst0000003'],
        'genotype': 'blahblah'
        }
    return testapp.post_json('/FlyDonor', item, status=201).json['@graph'][0]


@pytest.fixture
def donor_1(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def donor_2(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]

