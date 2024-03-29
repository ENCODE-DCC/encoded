import pytest


@pytest.fixture
def samtools_stats_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'average length': 100
    }
    return testapp.post_json('/samtools_stats_quality_metric', item).json['@graph'][0]