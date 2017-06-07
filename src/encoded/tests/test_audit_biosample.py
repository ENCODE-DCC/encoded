import pytest


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_mouse_biosample(testapp, lab, award, source, mouse):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': mouse['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_human_donor(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def base_chipmunk(testapp):
    item = {
        'name': 'chimpmunk',
        'taxon_id': '12345',
        'scientific_name': 'Chip chipmunicus'
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


def test_audit_biosample_constructs_whole_organism(testapp, base_biosample,
                                                   fly_donor, fly, construct):
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'whole organisms',
                                               'donor': fly_donor['@id'],
                                               'organism': fly['@id'],
                                               'transfection_method': 'chemical',
                                               'transfection_type': 'stable',
                                               'constructs': [construct['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched constructs' for error in errors_list)


def test_audit_biosample_constructs_whole_organism_compliant(testapp, base_biosample,
                                                             fly_donor, fly, construct):
    testapp.patch_json(fly_donor['@id'], {'constructs': [construct['@id']]})
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'whole organisms',
                                               'donor': fly_donor['@id'],
                                               'organism': fly['@id']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'mismatched constructs' for error in errors_list)


def test_audit_biosample_term_ntr(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'NTR:0000022',
                                               'biosample_term_name': 'myocyte',
                                               'biosample_type': 'in vitro differentiated cells'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'NTR biosample' for error in errors_list)


def test_audit_biosample_culture_dates(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'primary cell',
                                               'culture_start_date': '2014-06-30',
                                               'culture_harvest_date': '2014-06-25'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'invalid dates' for error in errors_list)


def test_audit_biosample_donor(testapp, base_biosample):
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing donor' for error in errors_list)


def test_audit_biosample_donor_organism(testapp, base_biosample, base_human_donor, base_chipmunk):
    testapp.patch_json(base_biosample['@id'], {'donor': base_human_donor['@id'],
                                               'organism': base_chipmunk['@id']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent organism' for error in errors_list)


def test_audit_biosample_status(testapp, base_biosample, construct):
    testapp.patch_json(base_biosample['@id'], {'status': 'released',
                                               'transfection_method': 'chemical',
                                               'transfection_type': 'stable',
                                               'constructs': [construct['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched status' for error in errors_list)


def test_audit_biosample_term_id(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'CL:349829'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'biosample term-type mismatch' for error in errors_list)


def test_audit_biosample_tissue_term_id(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'EFO:349829'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'biosample term-type mismatch' for error in errors_list)


def test_audit_biosample_ntr_term_id(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'NTR:349829'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'invalid biosample term id' for error in errors_list)


def test_audit_biosample_originated_from_consistency(testapp, biosample, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'UBERON:0002369',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'tissue',
                                               'originated_from': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent biosample_term_id' for error in errors_list)


def test_audit_biosample_originated_from_consistency_ontology(testapp, biosample, base_biosample):
    testapp.patch_json(biosample['@id'], {'biosample_term_id': 'UBERON:0004264'})
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'UBERON:0002369',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'tissue',
                                               'originated_from': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent biosample_term_id' for error in errors_list)


def test_audit_biosample_originated_from_consistency_ontology_part_of_multicellular_organism(
        testapp, biosample, base_biosample):
    testapp.patch_json(biosample['@id'], {'biosample_term_id': 'UBERON:0000468'})
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'CL:0000121',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'tissue',
                                               'originated_from': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent biosample_term_id' for error in errors_list)


def test_audit_biosample_originated_from_consistency_ontology_part_of(testapp,
                                                                      base_biosample,
                                                                      biosample_1,
                                                                      biosample_2):
    testapp.patch_json(biosample_1['@id'], {'biosample_term_id': 'UBERON:0000468'})
    testapp.patch_json(biosample_2['@id'], {'biosample_term_id': 'UBERON:0002037',
                                            'originated_from': biosample_1['@id']})
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'CL:0000121',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'tissue',
                                               'originated_from': biosample_2['@id']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent biosample_term_id' for error in errors_list)
