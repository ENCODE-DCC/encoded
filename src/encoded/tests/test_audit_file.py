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
