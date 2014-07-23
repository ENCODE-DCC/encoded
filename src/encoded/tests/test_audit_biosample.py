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
def base_biosample2(testapp, lab, award, source, organism):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:0000033',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
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


def test_audit_biosample_term_ntr(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'NTR:0000022', 'biosample_term_name': 'myocyte', 'biosample_type': 'in vitro differentiated cells'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'NTR' for error in errors)


def test_audit_biosample_culture_dates(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'culture_start_date': '2014-06-30', 'culture_harvest_date': '2014-06-25'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'invalid dates' for error in errors)


def test_audit_biosample_donor(testapp, base_biosample):
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing donor' for error in errors)


def test_audit_biosample_donor_organism(testapp, base_biosample, base_human_donor, base_chipmunk):
    testapp.patch_json(base_biosample['@id'], {'donor': base_human_donor['@id'], 'organism': base_chipmunk['@id']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'organism mismatch' for error in errors)


def test_audit_subcellular(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'subcellular_fraction_term_name': 'nucleus', 'subcellular_fraction_term_id': 'GO:0005739'})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'subcellular term mismatch' for error in errors)


def test_audit_depleted_in(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'whole organisms', 'depleted_in_term_name': ['head', 'testis'], 'depleted_in_term_id': ['UBERON:0000473', 'UBERON:0000033']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'depleted_in term mismatch' for error in errors)


def test_audit_depleted_in_length(testapp, base_biosample):
    testapp.patch_json(base_biosample['@id'], {'biosample_type': 'whole organisms', 'depleted_in_term_name': ['head', 'testis'], 'depleted_in_term_id': ['UBERON:0000473']})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'depleted_in length mismatch' for error in errors)


def test_audit_rnai_transfection(testapp, base_biosample, rnai):
    testapp.patch_json(base_biosample['@id'], {'rnais': [rnai['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing transfection_type' for error in errors)


def test_audit_construct_transfection(testapp, base_biosample, construct):
    testapp.patch_json(base_biosample['@id'], {'constructs': [construct['@id']]})
    res = testapp.get(base_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing transfection_type' for error in errors)
