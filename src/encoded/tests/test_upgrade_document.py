import pytest


def test_document_0_upgrade(upgrader, document_0, publication):
    value = upgrader.upgrade('document', document_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['references'] == [publication['identifiers'][0]]


def test_document_upgrade_status(upgrader, document_1):
    value = upgrader.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_document_upgrade_status_encode2(upgrader, document_1):
    document_1['award'] = '366388ac-685d-415c-b0bb-834ffafdf094'
    value = upgrader.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_document_upgrade_status_deleted(upgrader, document_1):
    document_1['status'] = 'DELETED'
    value = upgrader.upgrade('document', document_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_document_upgrade_references(root, upgrader,
                                     document, document_3,
                                     publication,
                                     threadlocals, dummy_request):
    context = root.get_by_uuid(document['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('document', document_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['references'] == [publication['uuid']]


def test_document_upgrade_status_replaced(upgrader, document_base):
    document_base['status'] = 'replaced'
    document_base['schema_version'] = '7'
    value = upgrader.upgrade('document', document_base, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert value['status'] == 'deleted'
