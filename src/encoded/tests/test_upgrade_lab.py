import pytest


@pytest.fixture
def lab():
    return{
        'name': 'Fake Lab',
    }


@pytest.fixture
def lab_1(lab):
    item = lab.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def lab_5(lab):
    item = lab.copy()
    item.update({
        'schema_version': '5',
        'status': 'current',
    })
    return item


def test_lab_upgrade(upgrader, lab_1):
    value = upgrader.upgrade('lab', lab_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_lab_upgrade_5_6(upgrader, lab_5):
    value = upgrader.upgrade('lab', lab_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'released'
    lab_5['status'] = 'disabled'
    lab_5['schema_version'] = '5'
    value = upgrader.upgrade('lab', lab_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'deleted'
