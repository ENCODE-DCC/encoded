import pytest


@pytest.fixture
def chia_pet_align_quality_metric(testapp, award, encode_lab, analysis_step_run_chia_alignment, chia_bam):
    item = {
        "step_run": analysis_step_run_chia_alignment['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ChIA-PET',
        "quality_metric_of": [chia_bam['@id']],
        "total_rp": 90000000,
        "rp_bl": 76000000,
        "frp_bl": 0.33,
        "pet": 68582483,
        "um_pet": 126928363,
        "nr_pet": 6000000,
        "pet_red": 0.82
    }

    return testapp.post_json('/chia_pet_alignment_quality_metric', item).json['@graph'][0]
