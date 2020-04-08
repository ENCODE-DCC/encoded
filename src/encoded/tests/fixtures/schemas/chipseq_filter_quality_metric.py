import pytest


@pytest.fixture
def chipseq_filter_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'NRF': 0.1,
        'PBC1': 0.3,
        'PBC2': 11
    }

    return testapp.post_json('/chipseq-filter-quality-metrics', item).json['@graph'][0]
