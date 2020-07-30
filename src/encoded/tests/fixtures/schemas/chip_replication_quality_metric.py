import pytest


@pytest.fixture 
def chip_replication_quality_metric_1(award, lab):
    return{
        "step_run": "63b1b347-f008-4103-8d20-0e12f54d1882",
        "award": award["uuid"],
        "lab": lab["uuid"],
        "quality_metric_of": ["ENCFF003COS"],
        "IDR_dispersion_plot": "ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf"
    }


@pytest.fixture 
def chip_replication_quality_metric_borderline_replicate_concordance(testapp, award, lab, analysis_step_run_chip_encode4, file_bed_narrowPeak_chip_peaks):
    item = {
        "step_run": analysis_step_run_chip_encode4['@id'],
        "award": award["uuid"],
        "lab": lab["uuid"],
        "assay_term_name": 'ChIP-seq',
        "quality_metric_of": [file_bed_narrowPeak_chip_peaks['@id']],
        'rescue_ratio': 1,
        'self_consistency_ratio': 3
    }

    return testapp.post_json('/chip-replication-quality-metrics', item).json['@graph'][0]

