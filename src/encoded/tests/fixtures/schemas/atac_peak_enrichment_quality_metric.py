import pytest


@pytest.fixture
def atac_peak_enrichment_quality_metric_1():
    return {
        'fri_dhs': 0.5850612112943434,
        'fri_blacklist': 0.0013046877081284722,
        'fri_prom': 0.21434770162962138,
        'fri_enh': 0.37244791482996753,
    }


@pytest.fixture
def atac_peak_enrichment_quality_metric_2(
        testapp, encode_lab, award,
        file_bed_stable_peaks_atac,
        analysis_step_run_atac_encode4_pseudoreplicate_concordance
        ):
    item = {
        'step_run': analysis_step_run_atac_encode4_pseudoreplicate_concordance['@id'],
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'assay_term_name': 'ATAC-seq',
        'frip': 0.190123014448055,
        'min_size': 150,
        '25_pct': 435,
        '50_pct': 745,
        '75_pct': 1190,
        'max_size': 3963,
        'mean': 849.2865957832648,
        'quality_metric_of': [file_bed_stable_peaks_atac['@id']],
    }
    return testapp.post_json('/atac_peak_enrichment_quality_metric', item).json['@graph'][0]
