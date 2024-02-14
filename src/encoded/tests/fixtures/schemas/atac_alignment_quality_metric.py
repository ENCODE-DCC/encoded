import pytest


@pytest.fixture
def atac_alignment_quality_metric_low(testapp, award, encode_lab,
                                        analysis_step_run_atac_encode4_alignment,
                                        ATAC_bam):
    item = {
        "step_run": analysis_step_run_atac_encode4_alignment['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ATAC-seq',
        "quality_metric_of": [ATAC_bam['@id']],
        "pct_mapped_reads": 76,
        "nfr_peak_exists": False,
        "mapped_reads": 880479,

    }

    return testapp.post_json('/atac_alignment_quality_metric', item).json['@graph'][0]
