import pytest


@pytest.fixture
def rnai(lab, award, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'rnai_type': 'shRNA',
    }


@pytest.fixture
def rnai_1(rnai):
    item = rnai.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


def test_rnai_upgrade(app, rnai_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('rnai', rnai_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'in progress'


def test_rnai_upgrade_status_encode2(app, rnai_1):
    migrator = app.registry['migrator']
    rnai_1['award'] = '366388ac-685d-415c-b0bb-834ffafdf094'
    value = migrator.upgrade('rnai', rnai_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'released'


def test_rnai_upgrade_status_deleted(app, rnai_1):
    migrator = app.registry['migrator']
    rnai_1['status'] = 'DELETED'
    value = migrator.upgrade('rnai', rnai_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'deleted'
