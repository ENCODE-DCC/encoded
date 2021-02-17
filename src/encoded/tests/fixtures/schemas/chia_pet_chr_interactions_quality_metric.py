import pytest


@pytest.fixture
def chia_pet_chr_int_quality_metric(testapp, award, encode_lab, analysis_step_run_chia_interaction_calling, chia_chromatin_int):
    item = {
        "step_run": analysis_step_run_chia_interaction_calling['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ChIA-PET',
        "quality_metric_of": [chia_chromatin_int['@id']],
        "intra_inter_pet_ratio": 0.9,
        "intra_inter_clust_pet2_ratio": 9.41,
        "intra_inter_clust_pet5_ratio": 100.65,
        "intra_inter_clust_pet10_ratio": 2616.83
    }

    return testapp.post_json('/chia_pet_chr_interactions_quality_metric', item).json['@graph'][0]