import pytest


@pytest.fixture
def chip_seq_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric(testapp, analysis_step_run_bam, file6, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file6['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric_2(testapp, analysis_step_run_bam, file7, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file7['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]
