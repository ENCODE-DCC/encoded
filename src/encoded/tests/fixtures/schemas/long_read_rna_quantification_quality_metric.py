import pytest


@pytest.fixture
def long_read_rna_quantification_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'genes_detected': 5000,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/long_read_rna_quantification_quality_metric', item).json['@graph'][0]
