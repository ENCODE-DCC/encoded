import pytest


@pytest.fixture
def atac_replication_quality_metric_borderline_replicate_concordance(testapp, award, encode_lab,
                                                    analysis_step_run_atac_encode4_partition_concordance,
                                                    file_bed_replicated_peaks_atac):
    item = {
        'step_run': analysis_step_run_atac_encode4_partition_concordance['@id'],
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'assay_term_name': 'ATAC-seq',
        'quality_metric_of': [file_bed_replicated_peaks_atac['@id']],
        'rescue_ratio': 1,
        'self_consistency_ratio': 3,
        'reproducible_peaks': 1000,
    }

    return testapp.post_json('/atac_replication_quality_metric', item).json['@graph'][0]


@pytest.fixture
def atac_replication_quality_metric_high_peaks(testapp, award, encode_lab,
                                               analysis_step_run_atac_encode4_partition_concordance,
                                               ATAC_bam2):
    item = {
        'step_run': analysis_step_run_atac_encode4_partition_concordance['@id'],
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'assay_term_name': 'ATAC-seq',
        'quality_metric_of': [ATAC_bam2['@id']],
        'rescue_ratio': 3,
        'self_consistency_ratio': 3,
        'reproducible_peaks': 200000,
    }

    return testapp.post_json('/atac_replication_quality_metric', item).json['@graph'][0]


@pytest.fixture
def atac_rep_metric_peaks_only(testapp, award, encode_lab, ATAC_bam2,
                               analysis_step_run_atac_encode4_partition_concordance):
    item = {
        'step_run': analysis_step_run_atac_encode4_partition_concordance['@id'],
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'assay_term_name': 'ATAC-seq',
        'quality_metric_of': [ATAC_bam2['@id']],
        'reproducible_peaks': 10000000,
    }

    return testapp.post_json('/atac_replication_quality_metric', item).json['@graph'][0]