import pytest


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        "biosample_term_name": "heart",
        'biosample_type': 'tissue',
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_mouse_biosample(testapp, lab, award, source, mouse, liver):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        "biosample_term_name": "liver",
        'biosample_type': 'tissue',
        'biosample_ontology': liver['uuid'],
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


@pytest.fixture
def ontology():
    ontology = {
        'UBERON:0002469': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:0001096',
                'UBERON:1111111'
            ]
        },
        'UBERON:1111111': {
            'part_of': []
        },
        'UBERON:0001096': {
            'part_of': []
        },
        'UBERON:0001043': {
            'part_of': [
                'UBERON:0001007',
                'UBERON:0004908'
            ]
        },
        'UBERON:0001007': {
            'part_of': []
        },
        'UBERON:0004908': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:1234567'
            ]
        },
        'UBERON:1234567': {
            'part_of': [
                'UBERON:0006920'
            ]
        },
        'UBERON:0006920': {
            'part_of': []
        },
        'UBERON:1231231': {
            'name': 'liver'
        }
    }
    return ontology


def test_audit_biosample_modifications_whole_organism(
        testapp, base_biosample,
        fly_donor, fly, construct_genetic_modification,
        construct_genetic_modification_N, whole_organism):
    testapp.patch_json(fly_donor['@id'], {
        'genetic_modifications': [construct_genetic_modification_N['@id']]})
    testapp.patch_json(base_biosample['@id'], {
        'biosample_ontology': whole_organism['uuid'],
        'donor': fly_donor['@id'],
        'organism': fly['@id'],
        'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched genetic modifications' for error in errors_list)


def test_audit_biosample_modifications_whole_organism_duplicated(
        testapp, base_biosample,
        fly_donor, fly, construct_genetic_modification):
    testapp.patch_json(fly_donor['@id'], {
        'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(base_biosample['@id'], {
        'biosample_type': 'whole organisms',
        'donor': fly_donor['@id'],
        'organism': fly['@id'],
        'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] != 'duplicated genetic modifications' for error in errors_list)


def test_audit_biosample_term_ntr(testapp, base_biosample, cell_free):
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': cell_free['uuid']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'NTR biosample' for error in errors_list)


def test_audit_biosample_culture_dates(testapp, base_biosample, erythroblast):
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'primary cell',
                                               'culture_start_date': '2014-06-30',
                                               'culture_harvest_date': '2014-06-25',
                                               'biosample_term_id': 'NTR:0000022'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'invalid dates' for error in errors_list)
    assert any(error['category'] == 'biosample not from culture'
               for error in errors_list)

    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': erythroblast['uuid']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'biosample not from culture' for error in errors_list)
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


def test_audit_biosample_consistent_organism(testapp, base_biosample, base_human_donor):
    testapp.patch_json(base_biosample['@id'], {'donor': base_human_donor['@id']})
    r = testapp.get(base_biosample['@id'] + '@@index-data')
    audits = r.json['audit']
    assert all(
        [
            detail['category'] != 'inconsistent organism'
            for audit in audits.values() for detail in audit
        ]
    )


def test_audit_biosample_status(testapp, base_biosample, construct_genetic_modification):
    testapp.patch_json(base_biosample['@id'], {
        'status': 'released',
        'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched status' for error in errors_list)


def test_audit_biosample_ntr_term_id(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'NTR:349829'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'invalid biosample term id' for error in errors_list)


def test_audit_biosample_part_of_consistency(testapp, biosample, base_biosample, ileum):
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': ileum['uuid'],
                                               'part_of': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent BiosampleType term' for error in errors_list)


def test_audit_biosample_part_of_consistency_ontology(testapp, biosample, base_biosample, ileum):
    testapp.patch_json(biosample['biosample_ontology'], {'term_id': 'UBERON:0004264'})
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': ileum['uuid'],
                                               'part_of': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent BiosampleType term' for error in errors_list)


def test_audit_biosample_part_of_consistency_ontology_part_of_multicellular_organism(testapp,
                                                                                     biosample,
                                                                                     base_biosample):
    testapp.patch_json(biosample['@id'], {'biosample_term_id': 'UBERON:0000468'})
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'CL:0000121',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'primary cell',
                                               'part_of': biosample['@id']})

    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent biosample_term_id' for error in errors_list)


def test_audit_biosample_part_of_consistency_ontology_part_of(testapp,
                                                              base_biosample,
                                                              biosample_1,
                                                              biosample_2):
    testapp.patch_json(biosample_1['@id'], {'biosample_term_id': 'UBERON:0000468'})
    testapp.patch_json(biosample_2['@id'], {'biosample_term_id': 'UBERON:0002037',
                                            'part_of': biosample_1['@id']})
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'CL:0000121',
                                               'biosample_term_name': 'adrenal gland',
                                               'biosample_type': 'primary cell',
                                               'part_of': biosample_2['@id']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent biosample_term_id' for error in errors_list)


def test_audit_biosample_phase(testapp, base_biosample, single_cell):
    target_err_cat = 'biosample cannot have defined cell cycle phase'

    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'single cell',
                                               'phase': 'G1'})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert any(error['category'] == target_err_cat
               for error_cat in errors.values()
               for error in error_cat)

    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': single_cell['uuid']})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert all(error['category'] != target_err_cat
               for error_cat in errors.values()
               for error in error_cat)


def test_audit_biosample_pmi(testapp, base_biosample, single_cell):
    target_err_cat = 'non-tissue sample has PMI'

    testapp.patch_json(base_biosample['@id'], {'PMI': 10,
                                               'PMI_units': 'day'})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert all(error['category'] != target_err_cat
               for error_cat in errors.values()
               for error in error_cat)

    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': single_cell['uuid']})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert any(error['category'] == target_err_cat
               for error_cat in errors.values()
               for error in error_cat)


def test_audit_biosample_cell_isolation_method(testapp, base_biosample, single_cell):
    target_err_cat = 'non-cell sample has cell_isolation_method'

    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'single cell',
                                               'cell_isolation_method': 'micropipetting'})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert any(error['category'] == target_err_cat
               for error_cat in errors.values()
               for error in error_cat)

    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': single_cell['uuid']})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert all(error['category'] != target_err_cat
               for error_cat in errors.values()
               for error in error_cat)


def test_audit_biosample_depleted_in_term_name(testapp, base_biosample, single_cell):
    target_err_cat = 'non-tissue sample has parts depleted'

    testapp.patch_json(base_biosample['@id'],
                       {'depleted_in_term_name': ['adult maxillary segment']})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert all(error['category'] != target_err_cat
               for error_cat in errors.values()
               for error in error_cat)

    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': single_cell['uuid']})
    errors = testapp.get(base_biosample['@id'] + '@@index-data').json['audit']
    assert any(error['category'] == target_err_cat
               for error_cat in errors.values()
               for error in error_cat)


def test_is_part_of_grandparent(ontology):
    from encoded.audit.biosample import is_part_of
    assert is_part_of('UBERON:0002469', 'UBERON:0001007', ontology)

def test_is_part_of_avoid_infinite_recursion(ontology):
    from encoded.audit.biosample import is_part_of
    assert is_part_of('UBERON:0002469', 'UBERON:0006920', ontology)

def test_is_part_of_not_related(ontology):
    from encoded.audit.biosample import is_part_of
    assert not is_part_of('UBERON:1111111', 'UBERON:0001043', ontology)

def test_is_part_of_part_of_not_in_ontology(ontology):
    from encoded.audit.biosample import is_part_of
    assert not is_part_of('UBERON:1231231', 'UBERON:0001043', ontology)

def test_is_part_of_empty_part_of_in_ontology(ontology):
    from encoded.audit.biosample import is_part_of
    assert not is_part_of('UBERON:0001007', 'UBERON:0001043', ontology)

def test_is_part_of_parent(ontology):
    from encoded.audit.biosample import is_part_of
    assert is_part_of('UBERON:0002469', 'UBERON:0001043', ontology)
