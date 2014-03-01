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
def experiment_2(root, experiment, files):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properites.copy()
    properties.update({
        'schema_version': '2',
        'encode2_dbxrefs': ['wgEncodeEH0020303'],
        'geo_dbxrefs': ['GSM999292'],
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

def test_experiment_upgrade_dbxrefs(root, registry, experiment, experiment_2, files, threadlocals, dummy_reques):
    migrator = registry['migrator']
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('experiment', experiment_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['ucsc_encode_db:wgEncodeEH0020303', 'geo_db:GSM999292']

