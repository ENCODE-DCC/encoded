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


def test_lab_upgrade(upgrader, lab_1):
    value = upgrader.upgrade('lab', lab_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
