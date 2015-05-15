import pytest


@pytest.fixture
def workflow_run(pipeline):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
    }

@pytest.fixture
def workflow_run_1(workflow_run):
    item = workflow_run.copy()
    item.update({
        'dx_workflow_id': "analysis-fake",
        'dx_analysis_id': "",
        'dx_workflow_json': { "nothing at all": "something that Cricket doesn't specify"},
        'schema_version': '1'
    })
    return item


def test_workflow_run_upgrade_1(app, workflow_run_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('workflow_run', workflow_run_1, current_version=workflow_run_1['schema_version'], target_version='2')
    assert value['schema_version'] == '2'
    assert value['dx_analysis_id'] == 'analysis-fake'
    assert value.get('dx_workflow_id') is None
    assert value.get('dx_workflow_json') is None
