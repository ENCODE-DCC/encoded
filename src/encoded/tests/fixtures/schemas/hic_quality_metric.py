import pytest


@pytest.fixture
def hic_quality_metric_single_ended_1(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'run_type': 'single-ended',
        "library_complexity_estimate_1_alignment": 323232,
        "library_complexity_estimate_2_alignments": 4534534,
        "library_complexity_estimate_1_and_2_alignments": 382948,
        "2_alignment_duplicates": 332433,
        "2_alignment_unique": 1123,
        "0_alignments": 23222,
        "pct_0_alignments": 0.2,
        "pct_1_alignment_unique": 0.1,
        "pct_1_alignment_duplicates": 0.33,
        "pct_sequenced_1_alignment_unique": 5.8,
        "pct_sequenced_1_alignment_duplicates": 4.7,
        "pct_sequenced_2_alignment_unique": 0.22,
        "pct_2_alignment_duplicates": 89.2,
        "pct_2_alignment_unique": 12.3,
        "pct_1_alignment": 0.1,
        "sequenced_reads": 3342,
        "1_alignment": 23493,
        "1_alignment_unique": 38444,
        "1_alignment_duplicates": 3443,
    }


@pytest.fixture
def hic_quality_metric_paired_ended_1(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'run_type': 'paired-ended',
        "avg_insert_size": 21,
        "below_mapq_threshold": 21,
        "library_complexity_estimate": 21,
        "sequenced_read_pairs": 12344441321,
        "2_alignments_a_b": 987987846,
        "pct_2_alignments_a_b": 95.3,
        "2_alignments_a1_a2b_a1b2_b1a2": 3545,
        "pct_2_alignments_a1_a2b_a1b2_b1a2": 1.2,
        "3_or_more_alignments": 45,
        "one_or_both_reads_unmapped": 22,
        "pct_one_or_both_reads_unmapped": 21
    }


@pytest.fixture
def hic_quality_metric_paired_ended_2(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'chimeric_ambiguous': 234,
    }


@pytest.fixture
def hic_quality_metric_single_ended_2(testapp, analysis_step_run, file, award, lab, hic_chromatin_int):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [hic_chromatin_int['@id']],
        'run_type': 'single-ended',
        'total_unique': 10000,
        'pct_unique_hic_contacts': 45,
        'pct_unique_long_range_greater_than_20kb': 10
    }
    return testapp.post_json('/hic_quality_metric', item).json['@graph'][0]


@pytest.fixture
def hic_quality_metric_paired_ended_3(testapp, analysis_step_run, file, award, lab, hic_chromatin_int):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [hic_chromatin_int['@id']],
        'run_type': 'paired-ended',
        'sequenced_read_pairs': 9000,
        'pct_unique_total_duplicates': 80,
        'pct_unique_hic_contacts': 30,
        'pct_ligation_motif_present': 3,
        'pct_unique_long_range_greater_than_20kb': 10
    }
    return testapp.post_json('/hic_quality_metric', item).json['@graph'][0]
