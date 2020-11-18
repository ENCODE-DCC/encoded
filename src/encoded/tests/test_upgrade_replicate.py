
def test_replicate_upgrade(root, upgrader, replicate_url, replicate_4, library_url, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate_url['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_4,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library_url['status']
    assert 'paired_ended' not in value


def test_replicate_upgrade_read_length(root, upgrader, replicate_url, replicate_5, library_url, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate_url['uuid'])
    dummy_request.context = context
    replicate_5['read_length'] = 36
    replicate_5['read_length_units'] = 'nt'
    value = upgrader.upgrade('replicate', replicate_5,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library_url['status']
    assert value['paired_ended'] is False


def test_replicate_upgrade_flowcell(root, upgrader, replicate_url, replicate_3, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate_url['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_3,
                             target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert 'flowcell_details' not in value
    assert 'machine' in value['notes']
    assert 'Test notes' in value['notes']


def test_replicate_upgrade_platform_etc(root, upgrader, replicate_url, replicate_5, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate_url['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_5,
                             target_version='5', context=context)
    assert value['schema_version'] == '5'
    assert 'platform' not in value
    assert 'read_length' not in value
    assert 'read_length_units' not in value
    assert 'paired_ended' not in value
    assert 'platform' in value['notes']
    assert 'Test notes' in value['notes']


def test_replicate_upgrade_status_8_9(root, upgrader, replicate_8):
    value = upgrader.upgrade('replicate', replicate_8, current_version='8',
                             target_version='9')
    assert value['schema_version'] == '9'
    assert value['status'] == 'in progress'
