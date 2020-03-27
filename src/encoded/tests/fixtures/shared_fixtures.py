import pytest
from ..constants import RED_DOT

'''
    This file is for fixtures that have no specific schema and can be shared across multiples test
'''


@pytest.fixture
def attachment():
    return {'download': 'red-dot.png', 'href': RED_DOT}


@pytest.fixture
def gm_characterization(testapp, award, lab, construct_genetic_modification_N, attachment):
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]


@pytest.fixture
def fastq_no_replicate(award, experiment, lab, platform1):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'fastq',
        'platform': platform1['@id'],
        'file_size': 23242,
        'run_type': 'paired-ended',
        'paired_end': '1',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }
