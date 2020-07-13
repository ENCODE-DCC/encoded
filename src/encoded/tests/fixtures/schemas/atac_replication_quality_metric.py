import pytest


@pytest.fixture 
def atac_replication_quality_metric_borderline_replicate_concordance(testapp, award, encode_lab,
                                                    analysis_step_run_atac_encode4_replicate_concordance,
                                                    file_bed_replicated_peaks_atac):
    item = {
        'step_run': analysis_step_run_atac_encode4_replicate_concordance['@id'],
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'assay_term_name': 'ATAC-seq',
        'quality_metric_of': [file_bed_replicated_peaks_atac['@id']],
        'rescue_ratio': 1,
        'self_consistency_ratio': 3,
        'reproducible_peaks': 200000,
    }

    return testapp.post_json('/atac_replication_quality_metric', item).json['@graph'][0]
