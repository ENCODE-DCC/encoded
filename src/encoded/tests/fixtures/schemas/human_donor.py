import pytest


# also tests schema_formats generally
@pytest.fixture
def human_donor(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']        
    }

@pytest.fixture
def base_human_donor(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_1(testapp, award, lab, human):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': human['@id'],
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


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
def human_donor_1_0(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
    }

@pytest.fixture
def human_donor_1_1(human_donor_1_0):
    item = human_donor_1_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def human_donor_2(human_donor_1_0):
    item = human_donor_1_0.copy()
    item.update({
        'schema_version': '2',
        'age': '11.0'
    })
    return item


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
def human_donor_10(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'genetic_modifications': []
    })
    return properties


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


@pytest.fixture
def human_donor_11a(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '11',
        'ethnicity': 'Caucasian'
    })
    return properties


@pytest.fixture
def human_donor_11b(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '11',
        'ethnicity': 'Arab Indian'
    })
    return properties


@pytest.fixture
def human_donor_12(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '12',
        'ethnicity': ['Caucasian', 'Asian']
    })
    return properties
