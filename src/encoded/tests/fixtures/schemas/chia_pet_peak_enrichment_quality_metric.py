import pytest


@pytest.fixture
def chia_pet_peak_quality_metric(testapp, award, encode_lab, analysis_step_run_chia_peak_calling, chia_peaks):
    item = {
        "step_run": analysis_step_run_chia_peak_calling['@id'],
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "assay_term_name": 'ChIA-PET',
        "quality_metric_of": [chia_peaks['@id']],
        "binding_peaks": 7831
    }

    return testapp.post_json('/chia_pet_peak_enrichment_quality_metric', item).json['@graph'][0]