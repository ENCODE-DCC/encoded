import pytest


@pytest.fixture
def mouse_donor_to_test(testapp, lab, award, mouse):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }


@pytest.fixture
def mouse_donor(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': '3413218c-3d86-498b-a0a2-9a406638e786',
    }


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
def mouse_donor_2_6(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_1_6(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_1_1(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_2_1(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


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
def mouse_donor_10(root, mouse_donor):
    item = root.get_by_uuid(mouse_donor['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'parent_strains': []
    })
    return properties
