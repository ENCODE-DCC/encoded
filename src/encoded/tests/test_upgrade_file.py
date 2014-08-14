import pytest


@pytest.fixture
def file_base(experiment):
    return {
        'accession': 'ENCFF000TST',
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
    }


@pytest.fixture
def file_1(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def file_2(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'current',
        'download_path': 'bob.bigBed'
    })
    return item


@pytest.fixture
def file_3(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '3',
        'status': 'current',
    })
    return item

def test_file_upgrade(registry, file_1):
    migrator = registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_file_upgrade2(root, registry, file_2, file, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('file', file_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'

def test_file_upgrade3(root, registry, file_3, file, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('file', file_2, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['lab'] != '' 
    assert value['award'] != ''
