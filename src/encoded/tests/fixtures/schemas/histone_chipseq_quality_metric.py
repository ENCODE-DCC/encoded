import pytest


@pytest.fixture
def histone_chipseq_quality_metric_frip(
    testapp,
    award,
    lab,
    analysis_step_run_chip_encode4,
    file_bed_narrowPeak_chip_peaks2
):
    item = {
        "step_run": analysis_step_run_chip_encode4['@id'],
        "award": award["uuid"],
        "lab": lab["uuid"],
        "assay_term_name": 'ChIP-seq',
        "quality_metric_of": [file_bed_narrowPeak_chip_peaks2['@id']],
    }
    return testapp.post_json(
        '/histone-chipseq-quality-metrics', item
    ).json['@graph'][0]
