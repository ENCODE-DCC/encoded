import pytest


@pytest.fixture
def wgbs_quality_metric(testapp, analysis_step_run_bam, file_bed_methyl, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bed_methyl['@id']],
        'lambda C methylated in CHG context': '13.1%',
        'lambda C methylated in CHH context': '12.5%',
        'lambda C methylated in CpG context': '0.9%'}
    return testapp.post_json('/bismark_quality_metric', item).json['@graph'][0]


@pytest.fixture
def bismark_quality_metric_1(pipeline, analysis_step_run, bigbed):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1',
    }


@pytest.fixture
def bismark_quality_metric_2(pipeline, analysis_step_run, bigbed):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '3',
        'quality_metric_of': [bigbed['uuid']]
    }
