import pytest


@pytest.fixture
def document_0(publication):
    return {
        'references': [publication['identifiers'][0]],
    }


@pytest.fixture
def document_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'document_type': 'growth protocol',
    }


@pytest.fixture
def document_1(document_base):
    item = document_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def document_3(root, document, publication):
    item = root.get_by_uuid(document['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'references': [publication['identifiers'][0]],
    })
    return properties


def test_document_0_upgrade(registry, document_0, publication):
    migrator = registry['migrator']
    value = migrator.upgrade('document', document_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['references'] == [publication['identifiers'][0]]


def test_document_upgrade_status(registry, document_1):
    migrator = registry['migrator']
    value = migrator.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_document_upgrade_status_encode2(registry, document_1):
    migrator = registry['migrator']
    document_1['award'] = '366388ac-685d-415c-b0bb-834ffafdf094'
    value = migrator.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_document_upgrade_status_deleted(registry, document_1):
    migrator = registry['migrator']
    document_1['status'] = 'DELETED'
    value = migrator.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_document_upgrade_references(root, registry, document, document_3, publication, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(document['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('document', document_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['references'] == [publication['uuid']]
