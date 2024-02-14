import pytest


@pytest.fixture
def chip_align_enrich_quality_metric(
    testapp, 
    award,
    encode_lab,
    analysis_step_run_chip_encode4,
    file_bam_1_chip
):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        'quality_metric_of': [file_bam_1_chip['@id']],
        'award': award['@id'],
        'lab': encode_lab['@id'],
        "NSC": -2.492904,
        "RSC": 2.439918,
        "argmin_corr": 1500,
        "assay_term_name": "ChIP-seq",
        "auc": 0.21011248730329599,
        "ch_div": 0.23833110841762475,
        "corr_estimated_fragment_len": 0.331124436914152,
        "corr_phantom_peak": 0.2140991,
        "diff_enrich": 27.193290098336647,
        "elbow_pt": 0.7439370613991243,
        "estimated_fragment_len": 190,
        "jsd": 0.27725918355932416,
        "min_corr": 0.1328268,
        "pct_genome_enrich": 14.380110762340804,
        "phantom_peak": 55,
        "subsampled_reads": 15000000,
        "syn_auc": 0.4954396743271865,
        "syn_elbow_pt": 0.5005380593170351,
        "syn_jsd": 0.43093845259510244,
        "syn_x_intercept": 0.0,
        "x_intercept": 0.11435911789991403
    }

    return testapp.post_json('/chip_alignment_enrichment_quality_metric', item).json['@graph'][0]
