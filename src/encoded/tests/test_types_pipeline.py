import pytest


def test_analysis_step_name_calcprop(testapp, analysis_step):
    assert analysis_step['@id'] == '/analysis-steps/fastqc-step-v-1/'
    assert analysis_step['name'] == 'fastqc-step-v-1'
    assert analysis_step['major_version'] == 1


def test_analysis_step_version_name_calcprop(testapp, analysis_step, analysis_step_version):
    assert analysis_step_version['minor_version'] == 0
    assert analysis_step_version['name'] == 'fastqc-step-v-1-0'
    assert analysis_step_version['@id'] == '/analysis-step-versions/fastqc-step-v-1-0/'


@pytest.mark.parametrize(
    'status',
    [
        'released',
        'in progress',
        'archived',
        'deleted',
        'revoked',
    ]
)
def test_pipeline_statuses(status, testapp, pipeline):
    testapp.patch_json(pipeline['@id'], {'status': status})
    res = testapp.get(pipeline['@id'] + '@@embedded').json
    assert res['status'] == status


def test_pipeline_invalid_statuses(testapp, pipeline):
    with pytest.raises(Exception):
        testapp.patch_json(pipeline['@id'], {'status': 'active'})
