import pytest


@pytest.fixture
def base_analysis(testapp, file1, admin):
    item = {
        'files': [file1['@id']],
        'submitted_by': admin['@id'],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_1(testapp, file_bam_1_1, file_bam_2_1, admin):
    item = {
        'files': [file_bam_1_1['@id'], file_bam_2_1['@id']],
        'submitted_by': admin['@id'],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_2(testapp, file_bam_1_1, file_bam_2_1, bam_file, admin):
    item = {
        'files': [file_bam_1_1['@id'], file_bam_2_1['@id'], bam_file['@id']],
        'submitted_by': admin['@id'],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_released(testapp, file_bam_1_1, file_bam_2_1, bam_file, admin):
    item = {
        'files': [file_bam_1_1['@id'], file_bam_2_1['@id'], bam_file['@id']],
        'status': 'released',
        'submitted_by': admin['@id'],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]


@pytest.fixture
def analysis_released_2(testapp, file1, admin):
    item = {
        'files': [file1['@id']],
        'status': 'released',
        'submitted_by': admin['@id'],
    }
    return testapp.post_json('/analysis', item).json['@graph'][0]
