import pytest


@pytest.fixture
def gembs_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'conversion_rate': 0.05,
        'average_coverage': 2}
    return testapp.post_json('/gembs_alignment_quality_metric', item).json['@graph'][0]
