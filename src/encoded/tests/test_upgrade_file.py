import pytest


@pytest.fixture
def file_base(experiment):
    return {
        'accession': 'ENCFF000TST',
        'dataset': experiment['uuid'],
        'file_format': 'fasta',
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
        'download_path': 'bob.bigBed'
    })
    return item


@pytest.fixture
def file_4(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '4',
        'file_format': 'bed_bedMethyl',
        'download_path': 'bob.bigBed',
        'output_type': 'Base_Overlap_Signal'
    })
    return item


@pytest.fixture
def file_5(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '5',
        'file_format': 'bigWig',
        'output_type': 'signal of multi-mapped reads'
    })
    return item


@pytest.fixture
def file_7(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '7'
    })
    return item


def test_file_upgrade(upgrader, file_1):
    value = upgrader.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_file_upgrade2(root, upgrader, file_2, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('file', file_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_file_upgrade3(root, upgrader, file_3, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('file', file_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['lab'] != ''
    assert value['award'] != ''
    assert 'download_path' not in value


def test_file_upgrade4(root, upgrader, file_4, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    content_md5sum = '0123456789abcdef0123456789abcdef'
    fake_registry = {
        'backfill_2683': {file['md5sum']: content_md5sum},
    }
    value = upgrader.upgrade(
        'file', file_4, target_version='5', context=context, registry=fake_registry)
    assert value['schema_version'] == '5'
    assert value['file_format'] == 'bed'
    assert value['file_format_type'] == 'bedMethyl'
    assert value['output_type'] == 'base overlap signal'
    assert value['content_md5sum'] == content_md5sum


def test_file_upgrade5(root, upgrader, registry, file_5, file, threadlocals, dummy_request):
    #context = root.get_by_uuid(file['uuid'])
    #dummy_request.context = context
    value = upgrader.upgrade(
        'file', file_5, current_version='5', target_version='6', registry=registry)
    assert value['schema_version'] == '6'
    assert value['output_type'] == 'signal of all reads'


def test_file_upgrade7(upgrader, file_7):
    value = upgrader.upgrade('file', file_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
