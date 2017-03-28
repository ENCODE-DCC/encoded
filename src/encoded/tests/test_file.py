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
        'file_size': 23242,
        'run_type': 'paired-ended',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }


@pytest.fixture
def fastq(fastq_no_replicate, replicate):
    item = fastq_no_replicate.copy()
    item['replicate'] = replicate['@id']
    return item


def test_file_post_fastq_no_replicate(testapp, fastq_no_replicate):
    testapp.post_json('/file', fastq_no_replicate, status=422)


def test_file_post_fastq_with_replicate(testapp, fastq):
    testapp.post_json('/file', fastq, status=201)


@pytest.fixture
def mapped_run_type_on_fastq(award, experiment, lab):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'fastq',
        'file_size': 2535345,
        'run_type': 'paired-ended',
        'mapped_run_type': 'single-ended',
        'md5sum': '01234567890123456789abcdefabcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }


@pytest.fixture
def mapped_run_type_on_bam(award, experiment, lab):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'bam',
        'assembly': 'mm10',
        'file_size': 2534535,
        'mapped_run_type': 'single-ended',
        'md5sum': 'abcdef01234567890123456789abcdef',
        'output_type': 'alignments',
        'status': 'in progress',
    }


def test_file_post_mapped_run_type_on_fastq(testapp, mapped_run_type_on_fastq):
    testapp.post_json('/file', mapped_run_type_on_fastq, status=422)


def test_file_post_mapped_run_type_on_bam(testapp, mapped_run_type_on_bam):
    testapp.post_json('/file', mapped_run_type_on_bam, status=201)


@pytest.fixture
def file(testapp, award, experiment, lab, replicate):
    item = {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'tsv',
        'file_size': 2534535,
        'md5sum': '00000000000000000000000000000000',
        'output_type': 'raw data',
        'status': 'in progress',
    }
    res = testapp.post_json('/file', item)
    return res.json['@graph'][0]


@pytest.fixture
def fastq_pair_1(fastq):
    item = fastq.copy()
    item['paired_end'] = '1'
    return item


@pytest.fixture
def fastq_pair_1_paired_with(fastq_pair_1, file):
    item = fastq_pair_1.copy()
    item['paired_with'] = file['@id']
    return item


@pytest.fixture
def fastq_pair_2(fastq):
    item = fastq.copy()
    item['paired_end'] = '2'
    item['md5sum'] = '2123456789abcdef0123456789abcdef'
    return item


@pytest.fixture
def fastq_pair_2_paired_with(fastq_pair_2, fastq_pair_1):
    item = fastq_pair_2.copy()
    item['paired_with'] = 'md5:' + fastq_pair_1['md5sum']
    return item


@pytest.fixture
def external_accession(fastq_pair_1):
    item = fastq_pair_1.copy()
    item['external_accession'] = 'EXTERNAL'
    return item


def test_file_post_fastq_pair_1_paired_with(testapp, fastq_pair_1_paired_with):
    testapp.post_json('/file', fastq_pair_1_paired_with, status=422)


def test_file_post_fastq_pair_1(testapp, fastq_pair_1):
    testapp.post_json('/file', fastq_pair_1, status=201)


def test_file_post_fastq_pair_2_paired_with(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    testapp.post_json('/file', fastq_pair_1, status=201)
    testapp.post_json('/file', fastq_pair_2_paired_with, status=201)


def test_file_post_fastq_pair_2_paired_with_again(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    testapp.post_json('/file', fastq_pair_1, status=201)
    testapp.post_json('/file', fastq_pair_2_paired_with, status=201)
    item = fastq_pair_2_paired_with.copy()
    item['md5sum'] = '3123456789abcdef0123456789abcdef'
    testapp.post_json('/file', item, status=409)


def test_file_post_fastq_pair_2_no_pair_1(testapp, fastq_pair_2):
    testapp.post_json('/file', fastq_pair_2, status=422)


def test_file_paired_with_back_calculated(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    res = testapp.post_json('/file', fastq_pair_1, status=201)
    location1 = res.json['@graph'][0]['@id']
    res = testapp.post_json('/file', fastq_pair_2_paired_with, status=201)
    location2 = res.json['@graph'][0]['@id']
    res = testapp.get(location1)
    assert res.json['paired_with'] == location2


def test_file_external_accession(testapp, external_accession):
    res = testapp.post_json('/file', external_accession, status=201)
    item = testapp.get(res.location).json
    assert 'accession' not in item
    assert item['@id'] == '/files/EXTERNAL/'


def test_file_technical_replicates(testapp, fastq_pair_1):
    res = testapp.post_json('/file', fastq_pair_1, status=201)
    location1 = res.json['@graph'][0]['@id']
    res = testapp.get(location1)
    assert res.json['technical_replicates'] == ['1_1']
