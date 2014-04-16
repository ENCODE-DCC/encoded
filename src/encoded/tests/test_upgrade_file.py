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
    assert value['status'] == 'released'


def test_file_upgrade_status_encode3(app, file_1):
    file_1['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    migrator = app.registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'in progress'
