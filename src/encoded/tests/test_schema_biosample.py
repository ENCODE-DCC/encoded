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
def biosample_depleted_in(mouse_biosample):
    item = mouse_biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'depleted_in_term_id': ["UBERON:0000033"],
        "biosample_type": "whole organisms"
    })
    return item


@pytest.fixture
def biosample_starting_amount(biosample):
    item = biosample.copy()
    item.update({
        'starting_amount': 'unknown'
    })
    return item


@pytest.fixture
def mouse_biosample(biosample, mouse):
    item = biosample.copy()
    item.update({
        'organism': mouse['uuid']
    })
    return item


def test_biosample_depleted_in(testapp, biosample_depleted_in):
    testapp.post_json('/biosample', biosample_depleted_in)


def test_biosample_depleted_in_name_required(testapp, biosample_depleted_in):
    del biosample_depleted_in['depleted_in_term_name']
    testapp.post_json('/biosample', biosample_depleted_in,  status=422)


def test_biosample_depleted_in_type_whole_organism(testapp, biosample_depleted_in):
    biosample_depleted_in['biosample_type'] = 'immortalized cell line'
    testapp.post_json('/biosample', biosample_depleted_in,  status=422)


def test_biosample_starting_amount(testapp, biosample_starting_amount):
    testapp.post_json('/biosample', biosample_starting_amount)


def test_biosample_transfection_method(testapp, biosample):
    biosample['transfection_method'] = 'transduction'
    testapp.post_json('/biosample', biosample, status=422)


def test_biosample_mouse_life_stage(testapp, mouse_biosample):
    mouse_biosample['mouse_life_stage'] = 'adult'
    testapp.post_json('/biosample', mouse_biosample)


def test_biosample_mouse_life_stage_fail(testapp, biosample):
    biosample['mouse_life_stage'] = 'adult'
    testapp.post_json('/biosample', biosample, status=422)
