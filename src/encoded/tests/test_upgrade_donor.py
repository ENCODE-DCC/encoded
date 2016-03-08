import pytest


@pytest.fixture
def human_donor(lab, award, organism):
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
def human_donor_1(human_donor):
    item = human_donor.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def human_donor_2(human_donor):
    item = human_donor.copy()
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


def test_human_donor_upgrade(upgrader, human_donor_1):
    value = upgrader.upgrade('human_donor', human_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'in progress'


def test_mouse_donor_upgrade_status_encode2(upgrader, mouse_donor_1):
    value = upgrader.upgrade('mouse_donor', mouse_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'released'


def test_donor_upgrade_status_deleted(upgrader, human_donor_1):
    human_donor_1['status'] = 'DELETED'
    value = upgrader.upgrade('human_donor', human_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'deleted'


def test_model_organism_donor_upgrade_(upgrader, mouse_donor_2):
    value = upgrader.upgrade('mouse_donor', mouse_donor_2, target_version='3')
    assert value['schema_version'] == '3'
    assert 'sex' not in value


def test_human_donor_age(upgrader, human_donor_2):
    value = upgrader.upgrade('human_donor', human_donor_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['age'] == '11'


def test_mouse_donor_upgrade_references(root, upgrader, mouse_donor, mouse_donor_3, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(mouse_donor['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('mouse_donor', mouse_donor_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['references'] == [publication['uuid']]


def test_mouse_donor_documents_upgrade(root, dummy_request, upgrader, mouse_donor, mouse_donor_3):
    context = root.get_by_uuid(mouse_donor['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('mouse_donor', mouse_donor_3, target_version='6', context=context)
    assert value['schema_version'] == '6'
    assert 'donor_documents' not in value
