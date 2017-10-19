import pytest


def replicate(submitter, award, lab, experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }


@pytest.fixture
def replicate_1(root, replicate, library):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '1',
        'library': library['uuid'],
        'paired_ended': False
    })
    return properties


@pytest.fixture
def replicate_2(root, replicate, library):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '2',
        'library': library['uuid'],
        'paired_ended': False
    })
    return properties


@pytest.fixture
def replicate_3(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'notes': 'Test notes',
        'flowcell_details': [
            {
                u'machine': u'Unknown',
                u'lane': u'2',
                u'flowcell': u'FC64KEN'
            },
            {
                u'machine': u'Unknown',
                u'lane': u'3',
                u'flowcell': u'FC64M2B'
            }
        ]
    })
    return properties


@pytest.fixture
def replicate_4(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '4',
        'notes': 'Test notes',
        'platform': 'encode:HiSeq 2000',
        'paired_ended': False,
        'read_length': 36,
        'read_length_units': 'nt'
    })
    return properties


@pytest.fixture
def replicate_8(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '8',
        'status': 'proposed'
    })
    return properties


def test_replicate_upgrade(root, upgrader, replicate, replicate_1, library, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_1,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library['status']
    assert 'paired_ended' not in value


def test_replicate_upgrade_read_length(root, upgrader, replicate, replicate_1, library, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    replicate_1['read_length'] = 36
    replicate_1['read_length_units'] = 'nt'
    value = upgrader.upgrade('replicate', replicate_1,
                             target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == library['status']
    assert value['paired_ended'] is False


def test_replicate_upgrade_flowcell(root, upgrader, replicate, replicate_3, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_3,
                             target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert 'flowcell_details' not in value
    assert 'machine' in value['notes']
    assert 'Test notes' in value['notes']


def test_replicate_upgrade_platform_etc(root, upgrader, replicate, replicate_4, threadlocals, dummy_request):
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('replicate', replicate_4,
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
