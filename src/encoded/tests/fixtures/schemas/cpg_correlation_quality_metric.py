import pytest


@pytest.fixture
def cpg_correlation_quality_metric(testapp, analysis_step_run_bam, file_bed_methyl, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bed_methyl['@id']],
        'Pearson correlation': 0.5}
    return testapp.post_json('/cpg_correlation_quality_metric', item).json['@graph'][0]
