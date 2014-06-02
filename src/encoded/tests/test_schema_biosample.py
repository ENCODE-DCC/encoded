import pytest


@pytest.fixture
def biosample(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def biosample_depeleted_in(biosample):
    item = biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'depleted_in_term_id': ["UBERON:0000033"],
        "biosample_type": "whole organisms"
    })
    return item


@pytest.fixture
def biosample_model_organism_dependencies(biosample):
    item = biosample.copy()
    item.update({
        'organism': "3413218c-3d86-498b-a0a2-9a406638e786",
        'model_organism_mating_status': 'virgin',
        'model_organism_age': '14.5',
        'model_organism_age_units': 'day',
        'model_organism_health_status': 'Healthy',
        'mouse_life_stage': 'embryonic',
        'model_organism_sex': 'mixed',
    })
    return item


def test_biosample_depeleted_in(testapp, biosample_depeleted_in):
    testapp.post_json('/biosample', biosample_depeleted_in)


def test_biosample_depeleted_in_name_required(testapp, biosample_depeleted_in):
    del biosample_depeleted_in['depleted_in_term_name']
    testapp.post_json('/biosample', biosample_depeleted_in,  status=422)


def test_biosample_depeleted_in_type_whole_organismg(testapp, biosample_depeleted_in):
    biosample_depeleted_in['biosample_type'] = 'tissue'
    testapp.post_json('/biosample', biosample_depeleted_in,  status=422)


def test_biosample_model_organism_dependencies(testapp, biosample_model_organism_dependencies):
    testapp.post_json('/biosample', biosample_model_organism_dependencies)


def test_biosample_model_organism_dependencies_human(testapp, biosample_model_organism_dependencies, organism ):
    biosample_model_organism_dependencies['organism'] = "organism['uuid']"
    testapp.post_json('/biosample', biosample_model_organism_dependencies, status=422)

def test_biosample_model_organism_dependencies_wrom_properties(testapp, biosample_model_organism_dependencies):
    biosample_model_organism_dependencies['worm_synchronization_stage'] = "fertilization"
    biosample_model_organism_dependencies['post_synchronization_time'] = "4"
    biosample_model_organism_dependencies['post_synchronization_time_units'] = "hour"
    testapp.post_json('/biosample', biosample_model_organism_dependencies, status=422)