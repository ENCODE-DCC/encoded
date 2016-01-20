import pytest


@pytest.fixture
def bigbed(testapp, lab, award, experiment, analysis_step_run):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'bedMethyl',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'methylation state at CpG',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
        'step_run': analysis_step_run['@id'],
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def bismark_quality_metric_1(pipeline, analysis_step_run, bigbed):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1',
    }


def test_bismark_quality_metric_upgrade_1(registry, bismark_quality_metric_1, bigbed):
    from contentbase import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('bismark_quality_metric', bismark_quality_metric_1, registry=registry, current_version='1', target_version='2')
    assert value['quality_metric_of'] == [bigbed['uuid']]
