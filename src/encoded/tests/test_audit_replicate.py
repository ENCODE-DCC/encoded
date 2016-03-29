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
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def non_concord_experiment(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample_type': 'immortalized cell line',
        'biosample_term_id': 'NTR:000945',
        'biosample_term_name': 'bad name'
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def non_concordant_rep(non_concord_experiment, library, testapp):
    item = {
        'experiment': non_concord_experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released',
        'library': library['uuid']
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


def test_audit_status_replicate(testapp, rep1):
    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched status' for error in errors_list)


def test_audit_replicate_library_with_documents(testapp, base_experiment, library_1,
                                                replicate_1_1, document):
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(library_1['@id'], {'documents': [document['@id']]})
    testapp.patch_json(library_1['@id'], {'fragmentation_method': 'chemical (DNaseI)'})

    res = testapp.get(replicate_1_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing documents' for error in errors_list)


def test_audit_replicate_library_missing_documents(testapp, base_experiment, library_1,
                                                   replicate_1_1):
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(library_1['@id'], {'fragmentation_method': 'see document'})
    res = testapp.get(replicate_1_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing documents' for error in errors_list)


def test_audit_replicate_library_wtih_general_documents(testapp, base_experiment,
                                                        library_1, replicate_1_1, document):
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(library_1['@id'], {'fragmentation_method': 'see document'})
    testapp.patch_json(document['@id'], {'document_type': 'general protocol'})
    testapp.patch_json(base_experiment['@id'], {'documents': [document['@id']]})

    res = testapp.get(replicate_1_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing documents' for error in errors_list)