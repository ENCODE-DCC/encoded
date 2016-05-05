import pytest


@pytest.fixture
def star_quality_metric(pipeline, analysis_step_run, bam_file):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '2',
        'quality_metric_of': [bam_file['uuid']]
    }


def test_star_quality_metric_upgrade(registry, star_quality_metric,
                                     bam_file, lab, award):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('star_quality_metric',
                             star_quality_metric, registry=registry,
                             current_version='2', target_version='3')
    assert value['lab'] == lab['@id'] and value['award'] == award['@id']
