import pytest


@pytest.fixture
def micro_rna_quantification_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'expressed_mirnas': 250,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/micro_rna_quantification_quality_metric', item).json['@graph'][0]
