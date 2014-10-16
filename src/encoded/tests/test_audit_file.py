import pytest


@pytest.fixture
def file1(experiment, award, lab, replicate, testapp):
    item = {
        'dataset': experiment['uuid'],
        'replicate': replicate['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'reads',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


def test_audit_paired_with(testapp, file1):
    testapp.patch_json(file1['@id'] + '?validate=false', {'paired_end': '2'})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing paired_with' for error in errors)


def test_audit_file_size(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing file_size' for error in errors)
