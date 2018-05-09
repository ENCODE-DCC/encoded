import pytest


@pytest.fixture
def target(organism):
    return{
        'organism': organism['uuid'],
        'label': 'TEST'
    }


@pytest.fixture
def target_1(target):
    item = target.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def target_2(target):
    item = target.copy()
    item.update({
        'schema_version': '2',
    })
    return item


@pytest.fixture
def target_5(target):
    item = target.copy()
    item.update({
        'schema_version': '5',
        'status': 'proposed'
    })
    return item


@pytest.fixture
def target_6(target):
    item = target.copy()
    item.update({
        'schema_version': '6',
        'status': 'current',
        'investigated_as': ['histone modification', 'histone']
    })
    return item


def test_target_upgrade(upgrader, target_1):
    value = upgrader.upgrade('target', target_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_target_investigated_as_upgrade(upgrader, target_2):
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['transcription factor']


def test_target_investigated_as_upgrade_tag(upgrader, target_2):
    target_2['label'] = 'eGFP'
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['tag']


def test_target_investigated_as_upgrade_recombinant(upgrader, target_2):
    target_2['label'] = 'eGFP-test'
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == [
        'recombinant protein', 'transcription factor']


def test_target_upgrade_status_5_6(upgrader, target_5):
    value = upgrader.upgrade(
        'target', target_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'current'


def test_target_upgrade_remove_histone_modification_6_7(upgrader, target_6):
    value = upgrader.upgrade(
        'target', target_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert value['investigated_as'] == ['histone']


@pytest.mark.parametrize(
    'old_status, new_status',
    [
        ('current', 'released'),
        ('deleted', 'deleted'),
        ('replaced', 'deleted')
    ]
)
def test_target_upgrade_move_to_standard_status_7_8(old_status, new_status, upgrader, target):
    target.update({'status': old_status})
    value = upgrader.upgrade(
        'target',
        target,
        current_version='7',
        target_version='8'
    )
    assert value['schema_version'] == '8'
    assert value['status'] == new_status
