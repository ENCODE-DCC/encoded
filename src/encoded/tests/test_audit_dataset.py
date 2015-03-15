import pytest


@pytest.fixture
def dataset(award, lab, testapp):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/dataset', item, status=201).json['@graph'][0]


def test_audit_publication(testapp, dataset):
    testapp.patch_json(dataset['@id'], {'dataset_type': 'publication'})
    res = testapp.get(dataset['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing reference' for error in errors_list)
