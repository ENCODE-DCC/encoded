import pytest


@pytest.fixture
def file(experiment):
    return{
        'accession': 'ENCFF000TST',
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
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


@pytest.fixture
def file_2(file):
    item = file.copy()
    item.update({
        'schema_version': '2',
        'status': 'current',
        'download_path': 'bob.bigBed'
    })
    return item


def test_file_upgrade(app, file_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


@pytest.mark.xfail
def test_file_upgrade2(root, registry, file_2, file, threadlocals, dummy_request):

    # This is not working as I am not getting the experiment information
    migrator = registry['migrator']
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    dataset = root.get_by_uuid(file['dataset']['uuid'])
    value = migrator.upgrade('file', file_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'
    assert value['lab'] == dataset['lab']
    assert value['award'] == dataset['award']
