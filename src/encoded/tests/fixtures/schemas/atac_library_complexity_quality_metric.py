import pytest


@pytest.fixture 
def atac_library_complexity_quality_metric_poor(testapp, award, encode_lab,
                                                analysis_step_run_atac_encode4_alignment,
                                                ATAC_bam):
    item = {
        "step_run": analysis_step_run_atac_encode4_alignment['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ATAC-seq',
        "quality_metric_of": [ATAC_bam['@id']],
        "NRF": 0.6,
        "PBC1": 0.5,
        "PBC2": 2
    }

    return testapp.post_json('/atac_library_complexity_quality_metric', item).json['@graph'][0]
