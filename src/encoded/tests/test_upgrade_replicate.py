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


def test_replicate_upgrade(root, registry, replicate, replicate_1, library, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('replicate', replicate_1, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'
    assert 'paired_ended' not in value


def test_replicate_upgrade_read_length(root, registry, replicate, replicate_1, library, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    replicate_1['read_length'] = 36
    replicate_1['read_length_units'] = 'nt'
    value = migrator.upgrade('replicate', replicate_1, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'
    assert value['paired_ended'] == False
