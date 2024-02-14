import pytest


def test_lab_upgrade(upgrader, lab_1_0):
    value = upgrader.upgrade('lab', lab_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
