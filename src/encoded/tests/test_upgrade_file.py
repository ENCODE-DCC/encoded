import pytest


@pytest.fixture
def file(experiment):
    return{
        'accession': 'ENCFF000TST',
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'rawData',
    }


@pytest.fixture
def file_1(file):
    item = file.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


def test_file_upgrade(app, file_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_file_upgrade2(app, file_1):

    # Set the experiment to released
    file_1['dataset'].update({
        'status': 'released'
        })

    migrator = app.registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'

    # Reset the file and experiment to NOT released
    file_1['status'] = 'current'
    file_1['dataset'].update({
        'status': 'release_ready'
        })

    value = migrator.upgrade('file', file_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'    