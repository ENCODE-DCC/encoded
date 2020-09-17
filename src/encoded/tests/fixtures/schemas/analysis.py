import pytest


@pytest.fixture
def base_analysis(testapp, file1):
    item = {
        'files': [file1['@id']],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_1(testapp, file_bam_1_1, file_bam_2_1):
    item = {
        'files': [file_bam_1_1['@id'], file_bam_2_1['@id']],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_2(testapp, file_bam_1_1, file_bam_2_1, bam_file):
    item = {
        'files': [file_bam_1_1['@id'], file_bam_2_1['@id'], bam_file['@id']],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]
