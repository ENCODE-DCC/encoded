import pytest


def test_access_key_upgrade(upgrader, access_key_1):
    value = upgrader.upgrade('access_key', access_key_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
