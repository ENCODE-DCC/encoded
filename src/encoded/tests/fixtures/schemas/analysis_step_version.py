import pytest


@pytest.fixture
def analysis_step_version_3(testapp, analysis_step, software_version):
    item = {
        'schema_version': '3',
        'version': 1,
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return item


@pytest.fixture
def analysis_step_version(testapp, analysis_step, software_version):
    item = {
        'analysis_step': analysis_step['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_bam(testapp, analysis_step_bam, software_version):
    item = {
        'analysis_step': analysis_step_bam['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_chip_encode4(testapp, analysis_step_chip_encode4, software_version):
    item = {
        'analysis_step': analysis_step_chip_encode4['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_atac_encode4_alignment(testapp, analysis_step_atac_encode4_alignment, software_version):
    item = {
        'analysis_step': analysis_step_atac_encode4_alignment['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_atac_encode4_replicate_concordance(testapp,
                analysis_step_atac_encode4_replicate_concordance, software_version):
    item = {
        'analysis_step': analysis_step_atac_encode4_replicate_concordance['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]
