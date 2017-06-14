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
        'assay_term_name': 'RNA-seq',
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


def test_audit_inconsistent_construct_tag(testapp, rep1,
                                          experiment, antibody_lot, target_H3K27ac,
                                          target, base_biosample, construct,
                                          library_1):
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': target_H3K27ac['@id']})
    testapp.patch_json(target['@id'], {'investigated_as': ['recombinant protein'],
                                       'label': 'FLAG'})
    testapp.patch_json(rep1['@id'], {'antibody': antibody_lot['@id'],
                                     'library': library_1['@id']})
    testapp.patch_json(base_biosample['@id'], {'constructs': [construct['@id']],
                                               'transfection_method': 'chemical',
                                               'transfection_type': 'stable'})

    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent construct tag' for error in errors_list)


def test_audit_consistent_construct_tag(testapp, rep1,
                                        experiment, antibody_lot,
                                        target, base_biosample, construct,
                                        library_1):
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': target['@id']})
    testapp.patch_json(target['@id'], {'investigated_as': ['recombinant protein'],
                                       'label': 'FLAG'})
    testapp.patch_json(rep1['@id'], {'antibody': antibody_lot['@id'],
                                     'library': library_1['@id']})
    testapp.patch_json(construct['@id'], {'tags': [{'name': 'FLAG', 'location': 'C-terminal'}]})
    testapp.patch_json(base_biosample['@id'], {'transfection_type': 'stable',
                                               'transfection_method': 'chemical',
                                               'constructs': [construct['@id']]})

    res = testapp.get(rep1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent construct tag' for error in errors_list)