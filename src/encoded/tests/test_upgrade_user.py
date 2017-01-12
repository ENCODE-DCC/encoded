import pytest


@pytest.fixture
def user():
    return{
        'first_name': 'Benjamin',
        'last_name': 'Hitz',
        'email': 'hitz@stanford.edu',
    }


@pytest.fixture
def user_1(user):
    item = user.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT'
    })
    return item


def test_user_upgrade(upgrader, user_1):
    value = upgrader.upgrade('user', user_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'


@pytest.fixture
def user_3(user):
    item = user.copy()
    item.update({
        'schema_version': '3',
        'viewing_groups': ['ENCODE'],
    })
    return item


def test_user_upgrade_viewing_groups(upgrader, user_3):
    value = upgrader.upgrade('user', user_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['viewing_groups'] == ['ENCODE3']
