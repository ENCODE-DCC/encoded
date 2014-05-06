import pytest


@pytest.fixture
def document_0():
    return {
        'references': ['PUBMED:19620212', 'PMID: 19122651']
    }


@pytest.fixture
def document(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'document_type': 'growth protocol',
    }


@pytest.fixture
def document_1(document):
    item = document.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


def test_document_0_upgrade(registry, document_0):
    migrator = registry['migrator']
    value = migrator.upgrade('document', document_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['references'] == ['PMID:19620212', 'PMID:19122651']


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
