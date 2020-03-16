import pytest


@pytest.fixture
def quality_metric_1(pipeline, analysis_step_run):
    return {
        'status': 'released',
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1'
    }
