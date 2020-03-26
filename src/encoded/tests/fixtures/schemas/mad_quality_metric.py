import pytest


@pytest.fixture
def mad_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.1,
        'MAD of log ratios': 3.1,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/mad_quality_metric', item).json['@graph'][0]
