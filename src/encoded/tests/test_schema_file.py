import pytest


@pytest.fixture
def file_no_replicate(testapp, experiment, award, lab):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'assembly': 'hg19',
        'md5sum': 'e002cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_with_replicate(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'assembly': 'hg19',
        'md5sum': 'e003cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_with_derived(testapp, experiment, award, lab, file_with_replicate):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'assembly': 'hg19',
        'file_size': 345,
        'md5sum': 'e004cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
        'derived_from': [file_with_replicate['@id']]
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_no_assembly(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'md5sum': '82847a2a5beb8095282c68c00f48e347',
        'output_type': 'alignments',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_no_error(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_content_error(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'output_type': 'reads',
        "read_length": 36,
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'content error'
    }
    return item


@pytest.fixture
def file_no_platform(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'output_type': 'reads',
        "read_length": 36,
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_no_paired_end(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'award': award['@id'],
        'platform': platform1['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_with_bad_date_created(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'date_created': '2017-10-23',
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }


def test_file_post(file_no_replicate):
    assert file_no_replicate['biological_replicates'] == []


def test_file_with_replicate_post(file_with_replicate):
    assert file_with_replicate['biological_replicates'] == [1]


def test_file_with_derived_from_post(testapp, file_with_derived):
    assert file_with_derived['biological_replicates'] == [1]


def test_file_no_assembly(testapp, file_no_assembly, file_with_replicate):
    res = testapp.post_json('/file', file_no_assembly, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(file_with_replicate['@id'],
                             {'file_format': 'fastq', 'output_type': 'reads'},
                             expect_errors=True)
    assert res.status_code == 422
    file_no_assembly['file_format'] = 'bigBed'
    file_no_assembly['file_format_type'] = 'narrowPeak'
    file_no_assembly['output_type'] = 'peaks'
    res = testapp.post_json('/file', file_no_assembly, expect_errors=True)
    assert res.status_code == 422


def test_not_content_error_without_message_ok(testapp, file_no_error):
    # status != content error, so an error detail message is not required.
    res = testapp.post_json('/file', file_no_error, expect_errors=False)
    assert res.status_code == 201


def test_content_error_without_message_bad(testapp, file_content_error):
    # status == content error, so an error detail message is required.
    res = testapp.post_json('/file', file_content_error, expect_errors=True)
    assert res.status_code == 422


def test_content_error_with_message_ok(testapp, file_content_error):
    # status == content error and we have a message, yay!
    file_content_error.update({'content_error_detail': 'Pipeline says error'})
    res = testapp.post_json('/file', file_content_error, expect_errors=False)
    assert res.status_code == 201


def test_not_content_error_with_message_bad(testapp, file_no_error):
    # We shouldn't use the error detail property if status != content error
    file_no_error.update({'content_error_detail': 'I am not the pipeline, I cannot use this.'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 422


def test_with_paired_end_1_2(testapp, file_no_error):
    # only sra files should be allowed to have paired_end == 1,2
    file_no_error.update({'paired_end': '1,2'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 422
    file_no_error.update({'file_format': 'sra'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 201


def test_fastq_no_platform(testapp, file_no_platform, platform1):
    res = testapp.post_json('/file', file_no_platform, expect_errors=True)
    assert res.status_code == 422
    file_no_platform.update({'platform': platform1['uuid']})
    res = testapp.post_json('/file', file_no_platform, expect_errors=True)
    assert res.status_code == 201


def test_with_run_type_no_paired_end(testapp, file_no_paired_end):
    res = testapp.post_json('/file', file_no_paired_end, expect_errors=True)
    assert res.status_code == 422
    file_no_paired_end.update({'paired_end': '1'})
    res = testapp.post_json('/file', file_no_paired_end, expect_errors=True)
    assert res.status_code == 201


def test_with_wrong_date_created(testapp, file_with_bad_date_created):
    res = testapp.post_json('/file', file_with_bad_date_created, expect_errors=True)
    assert res.status_code == 422


def test_no_file_available_md5sum(testapp, file_no_error):
    # Removing the md5sum from a file should not be allowed if the file exists
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 201

    item = file_no_error.copy()
    item.pop('md5sum', None)
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('md5sum', None)
    item.update({'no_file_available': True})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201

    item.update({'no_file_available': False})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422


def test_no_file_available_file_size(testapp, file_no_error):
    # Removing the file_size from a file should not be allowed if the file exists
    # and in one of the following states "in progress",  "revoked", "archived", "released"
    item = file_no_error.copy()
    item.pop('file_size', None)
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.update({'no_file_available': False})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.update({'status': 'upload failed'})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.pop('md5sum', None)
    item.update({'no_file_available': True})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201
