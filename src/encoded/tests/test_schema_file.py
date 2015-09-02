import pytest


@pytest.fixture
def file_no_replicate(testapp, experiment, award, lab):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
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
        'md5sum': 'e004cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
        'derived_from': [file_with_replicate['@id']],
    }
    return testapp.post_json('/file', item).json['@graph'][0]


def test_file_post(file_no_replicate):
    assert file_no_replicate['biological_replicates'] == []


def test_file_with_replicate_post(file_with_replicate):
    assert file_with_replicate['biological_replicates'] == [1]


def test_file_with_derived_from_post(testapp, file_with_derived):
    assert file_with_derived['biological_replicates'] == [1]
