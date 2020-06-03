import pytest


@pytest.fixture
def hotspot_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, encode_lab):
    item = {
        'SPOT1 score': 0.3345,
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'award': award['@id'],
        'lab': encode_lab['@id']
    }
    return testapp.post_json('/hotspot-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def hotspot_quality_metric_8(testapp, analysis_step_run_bam, file_bam_1_1, award, encode_lab):
    item = {
        'SPOT1 score': 0.5555,
        'award': award['@id'],
        'lab': encode_lab['@id'],
        'schema_version': 8
    }
    return item
