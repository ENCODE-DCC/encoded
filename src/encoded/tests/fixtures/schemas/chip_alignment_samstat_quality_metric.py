import pytest


@pytest.fixture
def chip_alignment_quality_metric_extremely_low_read_depth(testapp, analysis_step_run_chip_encode4, file_bam_1_chip, lab, award):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        "quality_metric_of": [file_bam_1_chip['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'mapped_reads': 10000,
        'total_reads': 30000,
        'processing_stage': 'filtered',
        'assay_term_name': 'ChIP-seq',
        'read1': 100, 
        'read2': 100
    }

    return testapp.post_json('/chip-alignment-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def chip_alignment_quality_metric_insufficient_read_depth(testapp, analysis_step_run_chip_encode4, file_bam_2_chip, lab, award):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        "quality_metric_of": [file_bam_2_chip['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'mapped_reads': 30000000,
        'total_reads': 30000000,
        'processing_stage': 'filtered',
        'assay_term_name': 'ChIP-seq',
        'read1': 100, 
        'read2': 100
    }

    return testapp.post_json('/chip-alignment-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def chip_alignment_quality_metric_extremely_low_read_depth_no_read1_read2(testapp, analysis_step_run_chip_encode4, file_bam_1_chip, lab, award):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        "quality_metric_of": [file_bam_1_chip['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'mapped_reads': 6000000,
        'total_reads': 6000000,
        'processing_stage': 'filtered',
        'assay_term_name': 'ChIP-seq',
    }

    return testapp.post_json('/chip-alignment-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def chip_alignment_quality_metric_insufficient_read_depth_no_read1_read2(testapp, analysis_step_run_chip_encode4, file_bam_2_chip, lab, award):
    item = {
        'step_run': analysis_step_run_chip_encode4['@id'],
        "quality_metric_of": [file_bam_2_chip['@id']],
        'award': award['@id'],
        'lab': lab['@id'],
        'mapped_reads': 11000000,
        'total_reads': 11000000,
        'processing_stage': 'filtered',
        'assay_term_name': 'ChIP-seq',
    }

    return testapp.post_json('/chip-alignment-quality-metrics', item).json['@graph'][0]