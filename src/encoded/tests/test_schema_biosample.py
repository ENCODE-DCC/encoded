import pytest


def test_biosample_depleted_in(testapp, biosample_depleted_in):
    testapp.post_json('/biosample', biosample_depleted_in)


def test_biosample_depleted_in_name_required(testapp, biosample_depleted_in):
    biosample_depleted_in.update({'depleted_in_term_id': ['UBERON:0000033']})
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


def test_biosample_mouse_life_stage_fail(testapp, biosample_data):
    biosample_data['mouse_life_stage'] = 'adult'
    testapp.post_json('/biosample', biosample_data, status=422)


def test_biosample_model_organism_props_on_human_fail(testapp, mouse_biosample, human):
    mouse_biosample['organism'] = human['uuid']
    testapp.post_json('/biosample', mouse_biosample, status=422)


def test_biosample_human_post_synchronization_fail(testapp, biosample_data):
    biosample_data['post_synchronization_time'] = '10'
    biosample_data['post_synchronization_time_units'] = 'hour'
    testapp.post_json('/biosample', biosample_data, status=422)


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


def test_biosample_human_whole_organism_fail(testapp, biosample_data, whole_organism):
    biosample_data['biosample_ontology'] = whole_organism['uuid']
    testapp.post_json('/biosample', biosample_data, status=422)


def test_alt_accession_ENCBS_regex(testapp, biosample_data):
    bio = testapp.post_json('/biosample', biosample_data).json['@graph'][0]
    res = testapp.patch_json(
        bio['@id'],
        {'status': 'replaced', 'alternate_accessions': ['ENCFF123ABC']}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {'status': 'replaced', 'alternate_accessions': ['ENCBS123ABC']})
    assert res.status_code == 200


def test_biosample_organoid_success(testapp, biosample_data, organoid):
    biosample_data['biosample_ontology'] = organoid['uuid']
    testapp.post_json('/biosample', biosample_data, status=201)


def test_biosample_post_diffentiation_props(testapp, biosample_data, organoid):
    biosample_data['biosample_ontology'] = organoid['uuid']
    bio = testapp.post_json('/biosample', biosample_data).json['@graph'][0]
    res = testapp.patch_json(
        bio['@id'],
        {'post_differentiation_time': 20},
        expect_errors=True
    )
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {'post_differentiation_time_units': 'hour'},
        expect_errors=True
    )
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {
            'post_differentiation_time': 20,
            'post_differentiation_time_units': 'hour'
        }
    )
    assert res.status_code == 200


def test_biosample_post_nucleic_acid_delivery_props(testapp, biosample_data):
    bio = testapp.post_json('/biosample', biosample_data).json['@graph'][0]
    res = testapp.patch_json(
        bio['@id'],
        {'post_nucleic_acid_delivery_time': 10},
        expect_errors=True
    )
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {'post_nucleic_acid_delivery_time_units': 'hour'},
        expect_errors=True
    )
    assert res.status_code == 422
    res = testapp.patch_json(
        bio['@id'],
        {
            'post_nucleic_acid_delivery_time': 10,
            'post_nucleic_acid_delivery_time_units': 'hour'
        }
    )
    assert res.status_code == 200


def test_biosample_disease_term_id(testapp, biosample_data):
    biosample_data.update({'disease_term_id': ['DOID:002']})
    testapp.post_json('/biosample', biosample_data, status=422)
    biosample_data.update({'disease_term_id': ['DOID:0080600']})
    testapp.post_json('/biosample', biosample_data, status=201)
