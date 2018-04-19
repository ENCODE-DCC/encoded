import pytest


@pytest.fixture
def biosample(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_term_name': 'heart',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def biosample_depleted_in(mouse_biosample):
    item = mouse_biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'biosample_term_name': 'multicellular organism',
        "biosample_type": "whole organisms"
    })
    return item


@pytest.fixture
def biosample_starting_amount(biosample):
    item = biosample.copy()
    item.update({
        'starting_amount': 20
    })
    return item


@pytest.fixture
def mouse_biosample(biosample, mouse):
    item = biosample.copy()
    item.update({
        'organism': mouse['uuid'],
        'model_organism_age': '8',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'model_organism_health_status': 'apparently healthy',
        'model_organism_mating_status': 'virgin'
    })
    return item


def test_biosample_depleted_in(testapp, biosample_depleted_in):
    testapp.post_json('/biosample', biosample_depleted_in)


def test_biosample_depleted_in_name_required(testapp, biosample_depleted_in):
    biosample_depleted_in.update({'depleted_in_term_id': ['UBERON:0000033']})
    testapp.post_json('/biosample', biosample_depleted_in,  status=422)


def test_biosample_depleted_in_type_whole_organism(testapp, biosample_depleted_in):
    biosample_depleted_in['biosample_type'] = 'whole organism'
    testapp.post_json('/biosample', biosample_depleted_in,  status=422)


def test_biosample_starting_amount_fail(testapp, biosample_starting_amount):
    testapp.post_json('/biosample', biosample_starting_amount, status=422)


def test_biosample_starting_amount_dep(testapp, biosample_starting_amount):
    biosample_starting_amount['starting_amount'] = 40
    biosample_starting_amount['starting_amount_units'] = 'cells'
    testapp.post_json('/biosample', biosample_starting_amount)


def test_biosample_mouse_life_stage(testapp, mouse_biosample):
    mouse_biosample['mouse_life_stage'] = 'adult'
    testapp.post_json('/biosample', mouse_biosample)


def test_biosample_mouse_life_stage_fail(testapp, biosample):
    biosample['mouse_life_stage'] = 'adult'
    testapp.post_json('/biosample', biosample, status=422)


def test_biosample_model_organism_props_on_human_fail(testapp, mouse_biosample, human):
    mouse_biosample['organism'] = human['uuid']
    testapp.post_json('/biosample', mouse_biosample, status=422)


def test_biosample_human_post_synchronization_fail(testapp, biosample):
    biosample['post_synchronization_time'] = '10'
    biosample['post_synchronization_time_units'] = 'hour'
    testapp.post_json('/biosample', biosample, status=422)


def test_biosample_mouse_post_synchronization_fail(testapp, mouse_biosample):
    mouse_biosample['post_synchronization_time'] = '10'
    mouse_biosample['post_synchronization_time_units'] = 'hour'
    testapp.post_json('/biosample', mouse_biosample, status=422)


def test_biosample_mating_status_no_sex_fail(testapp, mouse_biosample):
    del mouse_biosample['model_organism_sex']
    mouse_biosample['model_organism_mating_status'] = 'mated'
    testapp.post_json('/biosample', mouse_biosample, status=422)


def test_biosmple_post_synchronization_no_unit_fail(testapp, mouse_biosample, fly):
    mouse_biosample['organism'] = fly['uuid']
    mouse_biosample['post_synchronization_time'] = '30'
    testapp.post_json('/biosample', mouse_biosample, status=422)


def test_biosample_human_whole_organism_fail(testapp, biosample):
    biosample['biosample_type'] = 'whole organisms'
    testapp.post_json('/biosample', biosample, status=422)


def test_alt_accession_ENCBS_regex(testapp, biosample):
    bio = testapp.post_json('/biosample', biosample).json['@graph'][0]
    res = testapp.patch_json(
        bio['@id'],
        {'status': 'replaced', 'alternate_accessions': ['ENCFF123ABC']}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {'status': 'replaced', 'alternate_accessions': ['ENCBS123ABC']})
    assert res.status_code == 200


def test_biosample_tissue_cell_isolated_fail(testapp, biosample):
    biosample['cell_isolation_method'] = 'micropipetting'
    testapp.post_json('/biosample', biosample, status=422)


def test_biosample_tissue_cell_isolated_success(testapp, biosample):
    biosample['biosample_type'] = 'primary cell'
    biosample['biosample_term_id'] = 'CL:349829'
    biosample['cell_isolation_method'] = 'micropipetting'
    testapp.post_json('/biosample', biosample, status=201)