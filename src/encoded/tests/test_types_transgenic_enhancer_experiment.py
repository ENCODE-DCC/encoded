import pytest


def test_transgenic_enhancer_experiment_biosample_summary(testapp,
                                        transgenic_enhancer_experiment,
                                        biosample_1,
                                        biosample_2,
                                        treatment_5,
                                        whole_organism,
                                        mouse):
    testapp.patch_json(biosample_1['@id'], {'biosample_ontology': whole_organism['uuid'],
                                            'treatments': [treatment_5['@id']],
                                            'model_organism_age': '11.5',
                                            'model_organism_age_units': 'day',
                                            'mouse_life_stage': 'embryonic',
                                            'organism': mouse['@id']})
    testapp.patch_json(biosample_2['@id'], {'biosample_ontology': whole_organism['uuid'],
                                            'model_organism_age': '11.5',
                                            'model_organism_age_units': 'day',
                                            'mouse_life_stage': 'embryonic',
                                            'organism': mouse['@id']})
    testapp.patch_json(transgenic_enhancer_experiment['@id'], {'biosamples': [biosample_1['@id'], biosample_2['@id']]})
    res = testapp.get(transgenic_enhancer_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'whole organisms embryo (11.5 days) not treated and treated with ethanol'
