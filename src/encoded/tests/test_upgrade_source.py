import pytest


def test_source_upgrade(upgrader, source_1):
    value = upgrader.upgrade('source', source_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'
    assert 'award' not in value
    assert 'submitted_by' not in value
    assert 'lab' not in value


def test_source_upgrade_5_6(upgrader, source_5):
    value = upgrader.upgrade('source', source_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'released'
    source_5['status'] = 'disabled'
    source_5['schema_version'] = '5'
    value = upgrader.upgrade('source', source_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'deleted'
