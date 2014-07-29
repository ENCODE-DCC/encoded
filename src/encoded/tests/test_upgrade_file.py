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


@pytest.fixture
def file_2(file):
    item = file.copy()
    item.update({
        'schema_version': '2',
        'status': 'current',
    })
    return item


def test_file_upgrade(app, file_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_file_upgrade2(root, registry, file_2, experiment, threadlocals, dummy_request):

    migrator = registry['migrator']
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('file', file_2, experiment, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'
    assert value['lab'] == context['lab']
    assert value['award'] == context['award']
    # assert value['file_format'] == ''
