import pytest


def test_replicate_upgrade(root, upgrader, replicate, replicate_1_upgrade, library, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_1_upgrade,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library['status']
    assert 'paired_ended' not in value


def test_replicate_upgrade_read_length(root, upgrader, replicate, replicate_1_upgrade, library, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    replicate_1_upgrade['read_length'] = 36
    replicate_1_upgrade['read_length_units'] = 'nt'
    value = upgrader.upgrade('replicate', replicate_1_upgrade,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library['status']
    assert value['paired_ended'] is False


def test_replicate_upgrade_flowcell(root, upgrader, replicate, replicate_3_upgrade, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_3_upgrade,
                             target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert 'flowcell_details' not in value
    assert 'machine' in value['notes']
    assert 'Test notes' in value['notes']


def test_replicate_upgrade_platform_etc(root, upgrader, replicate, replicate_4_upgrade, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_4_upgrade,
                             target_version='5', context=context)
    assert value['schema_version'] == '5'
    assert 'platform' not in value
    assert 'read_length' not in value
    assert 'read_length_units' not in value
    assert 'paired_ended' not in value
    assert 'platform' in value['notes']
    assert 'Test notes' in value['notes']


def test_replicate_upgrade_status_8_9(root, upgrader, replicate_8_upgrade):
    value = upgrader.upgrade('replicate', replicate_8_upgrade, current_version='8',
                             target_version='9')
    assert value['schema_version'] == '9'
    assert value['status'] == 'in progress'
