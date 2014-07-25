import pytest


@pytest.fixture
def file1(experiment):
    return{
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'rawData',
        'status': 'released'
    }


def test_file_general_audit(testapp, file1):

    file2 = file.copy()

    file1['dataset'].update({
        'status': 'deleted'
        })
    res = testapp.post_json('/file', file1)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'status mismatch'

    file2['dataset'].update({
        'status': 'current'
        })
    res = testapp.post_json('/file', file2)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'status mismatch'
    assert error['category'] == 'missing lab'
    assert error['category'] == 'missing award'
    assert error['category'] == 'missing submitted_by'