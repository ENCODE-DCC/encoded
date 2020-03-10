import pytest
from ..constants import *

# TODO: Figure out biosample
@pytest.fixture
def biosample(testapp, source, lab, award, organism, heart):
    item = {
        'biosample_ontology': heart['uuid'],
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]


@pytest.fixture
def biosample_1(testapp, lab, award, source, organism, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_3(testapp, source, lab, award, organism, heart):
    item = {
        'biosample_ontology': heart['uuid'],
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]

@pytest.fixture
def biosample_type(a549):
    return a549


@pytest.fixture
def biosample_data(submitter, lab, award, source, human, brain):
    return {
        'award': award['@id'],
        'biosample_ontology': brain['uuid'],
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }

@pytest.fixture
def biosample_data2(submitter, lab, award, source, organism, heart):
    return {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }

@pytest.fixture
def biosample_depleted_in(mouse_biosample, whole_organism):
    item = mouse_biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'biosample_ontology': whole_organism['uuid'],
    })
    return item


@pytest.fixture
def biosample_starting_amount(biosample_data2):
    item = biosample_data2.copy()
    item.update({
        'starting_amount': 20
    })
    return item


@pytest.fixture
def mouse_biosample(biosample_data2, mouse):
    item = biosample_data2.copy()
    item.update({
        'organism': mouse['uuid'],
        'model_organism_age': '8',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'model_organism_health_status': 'apparently healthy',
        'model_organism_mating_status': 'virgin'
    })
    return item

@pytest.fixture
def biosample_1(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]

@pytest.fixture
def base_biosample_1(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
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
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': mouse['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


