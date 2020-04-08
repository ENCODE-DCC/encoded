import pytest


def test_user_upgrade_viewing_groups(upgrader, user_3):
    value = upgrader.upgrade('user', user_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['viewing_groups'] == ['ENCODE3']


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


def test_user_upgrade_8_to_9(upgrader, user_8):
    value = upgrader.upgrade('user', user_8, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert 'admin' in value['groups']
    assert 'verified' in value['groups']
    assert 'wrangler' not in value['groups']
