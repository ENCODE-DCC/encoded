import pytest


@pytest.fixture
def replicate_1(root, replicate, library):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '1',
        'library': library['uuid']
    })
    return properties


def test_replicate_upgrade(root, registry, replicate, replicate_1, library, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(replicate['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('replicate', replicate_1, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'
