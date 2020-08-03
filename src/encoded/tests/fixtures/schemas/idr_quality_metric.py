import pytest


@pytest.fixture
def enc3_chip_idr_quality_metric_insufficient_replicate_concordance(testapp, award, lab, analysis_step_run_chip_encode4, file_bed_narrowPeak_chip_peaks2):
    item = {
        "step_run": analysis_step_run_chip_encode4['@id'],
        "award": award["uuid"],
        "lab": lab["uuid"],
        "assay_term_name": 'ChIP-seq',
        "quality_metric_of": [file_bed_narrowPeak_chip_peaks2['@id']],
        'rescue_ratio': 3,
        'self_consistency_ratio': 3
    }

    return testapp.post_json('/idr-quality-metrics', item).json['@graph'][0]

