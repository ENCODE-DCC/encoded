import pytest


@pytest.fixture
def file1(experiment, award, lab):
    return{
        'dataset': experiment['uuid'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'reads',
        'award': award['uuid'],
        'lab': lab['uuid']
        'status': 'released'
    }
