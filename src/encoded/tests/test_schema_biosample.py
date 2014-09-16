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
def biosample_starting_amount(biosample):
    item = biosample.copy()
    item.update({
        'starting_amount': 'unknown'
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

def test_biosample_starting_amount(testapp, biosample_starting_amount):
    testapp.post_json('/biosample', biosample_starting_amount)

def test_biosample_transfection_method(testapp, biosample):
    biosample['transfection_method'] = 'transduction'
    testapp.post_json('/biosample', biosample, status=422)
