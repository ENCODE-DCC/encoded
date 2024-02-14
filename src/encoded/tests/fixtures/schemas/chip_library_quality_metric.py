import pytest


@pytest.fixture
def chip_library_quality_metric_severe_bottlenecking_poor_complexity(testapp, analysis_step_run_chip_encode4, file_bam_1_chip, lab, award):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        "quality_metric_of": [file_bam_1_chip['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'assay_term_name': 'ChIP-seq',
        'NRF': 0.4,
        'PBC1': 0.35,
        'PBC2': 0
    }

    return testapp.post_json('/chip-library-quality-metrics', item).json['@graph'][0]
