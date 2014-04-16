import pytest


@pytest.fixture
def human_donor(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
    }


@pytest.fixture
def mouse_donor(lab, award):
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
def mouse_donor_1(mouse_donor):
    item = mouse_donor.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


def test_human_donor_upgrade(app, human_donor_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('human_donor', human_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'in progress'


def test_mouse_donor_upgrade_status_encode2(app, mouse_donor_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('mouse_donor', mouse_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'released'


def test_donor_upgrade_status_deleted(app, human_donor_1):
    migrator = app.registry['migrator']
    human_donor_1['status'] = 'DELETED'
    value = migrator.upgrade('human_donor', human_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'deleted'
