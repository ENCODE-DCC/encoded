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


@pytest.fixture
def user_7(user):
    item = user.copy()
    item.update({
        'schema_version': '6',
        'phone1': '206-685-2672',
        'phone2': '206-267-1098',
        'fax': '206-267-1094',
        'skype': 'fake_id',
        'google': 'google',
        'timezone': 'US/Pacific',
    })
    return item


def test_user_upgrade_contact_info(upgrader, user_7):
    value = upgrader.upgrade('user', user_7, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert 'phone1' not in value
    assert 'phone2' not in value
    assert 'fax' not in value
    assert 'skype' not in value
    assert 'google' not in value
    assert 'timezone' not in value


def test_user_upgrade_7_to_8(upgrader, user_3):
    user_3['schema_version'] = '7'
    value = upgrader.upgrade('user', user_3, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert 'community' in value['viewing_groups']