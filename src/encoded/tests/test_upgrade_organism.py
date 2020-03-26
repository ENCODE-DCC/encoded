import pytest


def test_organism_upgrade(upgrader, organism_1_0):
    value = upgrader.upgrade('organism', organism_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_organism_upgrade_4_5(upgrader, organism_4_0):
    value = upgrader.upgrade('organism', organism_4_0, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'released'
    organism_4_0['status'] = 'disabled'
    organism_4_0['schema_version'] = '4'
    value = upgrader.upgrade('organism', organism_4_0, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'deleted'
