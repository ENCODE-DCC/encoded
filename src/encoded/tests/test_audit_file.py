import pytest


@pytest.fixture
def file1(experiment):
    return{
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'reads',
        'status': 'released'
    }


def test_file_general_audit(testapp, file1):

    #res = testapp.patch_json(file1['dataset'], {'status': 'deleted'})
    res = testapp.post_json('/file', file1)
    res = testapp.get(res.location + '@@index-data')
    #error, = res.json['audit']
    #assert error['category'] == 'status mismatch'
    #assert error['category'] == 'missing lab'
    #assert error['category'] == 'missing award'
    #assert error['category'] == 'missing submitted_by'
