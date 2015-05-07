import pytest


@pytest.fixture
def rep1(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def rep2(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released',
        'paired_ended': False,
        'read_length': 101
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


def test_audit_status_replicate(testapp, rep1):
    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched status' for error in errors_list)


def test_audit_item_replicate(testapp, rep2):
    res = testapp.get(rep2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'replicate with read_length' for error in errors_list)
