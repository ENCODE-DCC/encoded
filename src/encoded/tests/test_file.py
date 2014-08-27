import pytest


def test_reference_file_by_md5(testapp, file):
    res = testapp.get('/md5:{md5sum}'.format(**file)).follow(status=200)
    assert res.json['@id'] == file['@id']


def test_replaced_file_not_uniqued(testapp, file):
    testapp.patch_json('/{uuid}'.format(**file), {'status': 'replaced'}, status=200)
    testapp.get('/md5:{md5sum}'.format(**file), status=404)


@pytest.fixture
def fastq_no_replicate(award, experiment, lab):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }


@pytest.fixture
def fastq(award, experiment, lab, replicate):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }


def test_file_post_fastq_no_replicate(testapp, fastq_no_replicate):
    testapp.post_json('/file', fastq_no_replicate, status=422)


def test_file_post_fastq_with_replicate(testapp, fastq):
    testapp.post_json('/file', fastq, status=201)


@pytest.fixture
def file(testapp, award, experiment, lab, replicate):
    item = {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'tsv',
        'md5sum': '00000000000000000000000000000000',
        'output_type': 'raw data',
        'status': 'in progress',
    }
    res = testapp.post_json('/file', item)
    return res.json['@graph'][0]


@pytest.fixture
def fastq_pair_1(award, experiment, lab, replicate):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'paired_end': '1',
        'status': 'in progress',
    }


@pytest.fixture
def fastq_pair_1_paired_with(award, experiment, file, lab, replicate):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'paired_end': '1',
        'paired_with': file['@id'],
        'status': 'in progress',
    }


@pytest.fixture
def fastq_pair_2(award, experiment, lab, replicate):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'paired_end': '2',
        'status': 'in progress',
    }


@pytest.fixture
def fastq_pair_2_paired_with(award, experiment, file, lab, replicate):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'paired_end': '2',
        'paired_with': file['@id'],
        'status': 'in progress',
    }


def test_file_post_fastq_pair_1_paired_with(testapp, fastq_pair_1_paired_with):
    testapp.post_json('/file', fastq_pair_1_paired_with, status=422)


def test_file_post_fastq_pair_1(testapp, fastq_pair_1):
    testapp.post_json('/file', fastq_pair_1, status=201)


def test_file_post_fastq_pair_2_paired_with(testapp, fastq_pair_2_paired_with):
    testapp.post_json('/file', fastq_pair_2_paired_with, status=201)


def test_file_post_fastq_pair_2(testapp, fastq_pair_2):
    testapp.post_json('/file', fastq_pair_2, status=422)
