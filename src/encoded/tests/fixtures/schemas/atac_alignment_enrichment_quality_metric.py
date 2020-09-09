import pytest


@pytest.fixture
def atac_align_enrich_quality_metric_med(testapp, award, encode_lab,
                                        analysis_step_run_atac_encode4_alignment,
                                        ATAC_bam):
    item = {
        "step_run": analysis_step_run_atac_encode4_alignment['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ATAC-seq',
        "quality_metric_of": [ATAC_bam['@id']],
        "tss_enrichment": 6,
        "RSC": -1.2,
        "NSC": -0.2
    }

    return testapp.post_json('/atac_alignment_enrichment_quality_metric', item).json['@graph'][0]
