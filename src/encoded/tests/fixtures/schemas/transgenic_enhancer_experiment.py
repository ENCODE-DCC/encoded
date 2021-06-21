import pytest


@pytest.fixture
def transgenic_enhancer_experiment(testapp, lab, award, whole_organism, mouse_whole_organism_biosample):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'transgenic enhancer assay',
        'biosample_ontology': whole_organism['uuid'],
        'status': 'in progress',
        'biosamples': [mouse_whole_organism_biosample['@id']]
    }
    return testapp.post_json('/transgenic_enhancer_experiment', item).json['@graph'][0]

