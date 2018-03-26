import pytest


@pytest.mark.parametrize(
    'status',
    [
        'released',
        'in progress',
        'deleted',
    ]
)
def test_analysis_step_run_valid_statuses(status, testapp, analysis_step_run):
    testapp.patch_json(analysis_step_run['@id'], {'status': status})
    res = testapp.get(analysis_step_run['@id'] + '@@embedded').json
    assert res['status'] == status


def test_analysis_step_run_invalid_statuses(testapp, analysis_step_run):
    with pytest.raises(Exception):
        testapp.patch_json(analysis_step_run['@id'], {'status': 'virtual'})
