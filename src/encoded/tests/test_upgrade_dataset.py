import pytest

@pytest.fixture
def experiment_1(root, experiment, files):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    assert root.get_by_uuid(files[0]['uuid']).properties['dataset'] == str(item.uuid)
    assert root.get_by_uuid(files[1]['uuid']).properties['dataset'] != str(item.uuid)
    properties.update({
        'schema_version': '1',
        'files': [files[0]['uuid'], files[1]['uuid']]
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
        'aliases': [ 'ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
    })
    return properties


def test_experiment_upgrade(root, registry, experiment, experiment_1, files, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('experiment', experiment_1, target_version='2', context=context)
    assert value['schema_version'] == '2'
    assert 'files' not in value
    assert value['related_files'] == [files[1]['uuid']]

def test_experiment_upgrade_dbxrefs(root, registry, experiment, experiment_2, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('experiment', experiment_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-hg19:wgEncodeEH002945', 'GEO:GSM99494']

def test_experiment_upgrade_dbxrefs_mouse(root, registry, experiment, experiment_2, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    experiment_2['encode2_dbxrefs'] = ['wgEncodeEM008391'] 
    value = migrator.upgrade('experiment', experiment_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-mm9:wgEncodeEM008391', 'GEO:GSM99494']

def test_dataset_upgrade_dbxrefs(root, registry, dataset, dataset_2, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-mm9:wgEncodeCaltechTfbs']
    assert value['aliases'] == [ 'barbara-wold:mouse-TFBS']
    assert 'geo_dbxrefs' not in value

def test_dataset_upgrade_dbxrefs_human(root, registry, dataset, dataset_2, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    dataset_2['aliases'] = [ 'ucsc_encode_db:hg19-wgEncodeSydhTfbs']
    value = migrator.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-hg19:wgEncodeSydhTfbs']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value

def test_dataset_upgrade_dbxrefs_alias(root, registry, dataset, dataset_2, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(dataset['uuid'])
    dummy_request.context = context
    dataset_2['aliases'] = [ 'ucsc_encode_db:wgEncodeEH002945']
    value = migrator.upgrade('dataset', dataset_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-ENCODE-hg19:wgEncodeEH002945']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value