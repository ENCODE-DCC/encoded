import pytest


@pytest.fixture
def experiment_1(root, experiment, file, file_dataset):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    assert root.get_by_uuid(file['uuid']).properties['dataset'] == str(item.uuid)
    assert root.get_by_uuid(file_dataset['uuid']).properties['dataset'] != str(item.uuid)
    properties.update({
        'schema_version': '1',
        'files': [file['uuid'], file_dataset['uuid']]
    })
    del properties['related_files']
    return properties


@pytest.fixture
def experiment_2(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '2',
        'encode2_dbxrefs': ['wgEncodeEH002945'],
        'geo_dbxrefs': ['GSM99494'],
    })
    return properties


@pytest.fixture
def dataset_2(root, dataset):
    item = root.get_by_uuid(dataset['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '2',
        'aliases': ['ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
    })
    return properties


@pytest.fixture
def experiment_3(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'status': "DELETED",
    })
    return properties


@pytest.fixture
def dataset_3(root, dataset):
    item = root.get_by_uuid(dataset['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'status': 'CURRENT',
        'award': '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
    })
    return properties


@pytest.fixture
def dataset_5(root, dataset, publication):
    item = root.get_by_uuid(dataset['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '5',
        'references': [publication['identifiers'][0]],
    })
    return properties


def test_experiment_upgrade(root, upgrader, experiment, experiment_1, file_dataset, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_1, target_version='2', context=context)
    assert value['schema_version'] == '2'
    assert 'files' not in value
    assert value['related_files'] == [file_dataset['uuid']]


def test_experiment_upgrade_dbxrefs(root, upgrader, experiment, experiment_2, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-hg19:wgEncodeEH002945', 'GEO:GSM99494']


def test_experiment_upgrade_dbxrefs_mouse(root, upgrader, experiment, experiment_2, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    experiment_2['encode2_dbxrefs'] = ['wgEncodeEM008391']
    value = upgrader.upgrade('experiment', experiment_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-mm9:wgEncodeEM008391', 'GEO:GSM99494']


def test_dataset_upgrade_dbxrefs(root, upgrader, dataset, dataset_2, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-mm9:wgEncodeCaltechTfbs']
    assert value['aliases'] == ['barbara-wold:mouse-TFBS']
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_human(root, upgrader, dataset, dataset_2, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    dataset_2['aliases'] = [ 'ucsc_encode_db:hg19-wgEncodeSydhTfbs']
    value = upgrader.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-hg19:wgEncodeSydhTfbs']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_alias(root, upgrader, dataset, dataset_2, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    dataset_2['aliases'] = ['ucsc_encode_db:wgEncodeEH002945']
    value = upgrader.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-ENCODE-hg19:wgEncodeEH002945']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_experiment_upgrade_status(root, upgrader, experiment, experiment_3, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['status'] == 'deleted'


def test_dataset_upgrade_status(root, upgrader, dataset, dataset_3, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('dataset', dataset_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_status_encode3(root, upgrader, experiment, experiment_3, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    experiment_3['status'] = 'CURRENT'
    value = upgrader.upgrade('experiment', experiment_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_no_status_encode2(root, upgrader, dataset, dataset_3, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    del dataset_3['status']
    value = upgrader.upgrade('dataset', dataset_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_no_status_encode3(root, upgrader, experiment, experiment_3, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    del experiment_3['status']
    value = upgrader.upgrade('experiment', experiment_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_references(root, upgrader, dataset, dataset_5, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('dataset', dataset_5, target_version='6', context=context)
    assert value['schema_version'] == '6'
    assert value['references'] == [publication['uuid']]
