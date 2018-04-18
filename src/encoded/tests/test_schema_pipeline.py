import pytest


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
def test_pipeline_valid_statuses(status, testapp, pipeline):
    testapp.patch_json(pipeline['@id'], {'status': status})
    res = testapp.get(pipeline['@id'] + '@@embedded').json
    assert res['status'] == status


def test_pipeline_invalid_statuses(testapp, pipeline):
    with pytest.raises(Exception):
        testapp.patch_json(pipeline['@id'], {'status': 'active'})
