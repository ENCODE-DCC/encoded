import pytest


@pytest.mark.parametrize(
    'status',
    [
        'released',
        'in progress',
        'deleted'
    ]
)
def test_publication_valid_statuses(status, testapp, publication):
    testapp.patch_json(publication['@id'], {'status': status})
    res = testapp.get(publication['@id'] + '@@embedded').json
    assert res['status'] == status


@pytest.mark.parametrize(
    'status',
    [
        'archived',
        'revoked',
        'replaced'
    ]
)
def test_publication_invalid_statuses(status, testapp, publication):
    with pytest.raises(Exception):
        testapp.patch_json(publication['@id'], {'status': status})
