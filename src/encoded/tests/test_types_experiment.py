import pytest


def test_isogenic_replicate_type(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='isogenic' 

def test_anisogenic_replicate_type_sex_age_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'female' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic' 

def test_anisogenic_replicate_type_sex_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '15', 'life_stage': 'adult' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'female' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic' 

def test_anisogenic_replicate_type_age_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'mixed' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic'     

def test_anisogenic_replicate_type(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age': 'unknown' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'unknown' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic'   

def test_experiment_biosample_summary(testapp,
                                      base_experiment,
                                      donor_1,
                                      donor_2,
                                      biosample_1,
                                      biosample_2,
                                      library_1,
                                      library_2,
                                      treatment_5,
                                      replicate_1_1,
                                      replicate_2_1,
                                      s2r_plus,
                                      liver):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'day', 'age': '1', 'life_stage': 'child'})
    testapp.patch_json(donor_1['@id'], {'sex': 'female',
                                        "life_stage": "embryonic"})
    testapp.patch_json(donor_2['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'treatments': [treatment_5['@id']],
                                            'biosample_ontology': s2r_plus['uuid'],
                                            "subcellular_fraction_term_name": "nucleus",
                                            'pulse_chase_time': 2,
                                            'pulse_chase_time_units': 'hour',
                                            })
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            'biosample_ontology': liver['uuid'],
                                            'treatments': [treatment_5['@id']],
                                            'pulse_chase_time': 2,
                                            'pulse_chase_time_units': 'hour',
                                            })

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'S2R+ cell line nuclear fraction and ' + \
        'liver tissue male child (1 day), treated with ethanol, ' + \
        'subjected to a 2 hour pulse-chase'


def test_experiment_biosample_summary_2(testapp,
                                        base_experiment,
                                        donor_1,
                                        donor_2,
                                        biosample_1,
                                        biosample_2,
                                        library_1,
                                        library_2,
                                        treatment_5,
                                        replicate_1_1,
                                        replicate_2_1,
                                        liver):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_1['@id'], {'sex': 'male'})
    testapp.patch_json(donor_2['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'biosample_ontology': liver['uuid'],
                                            'treatments': [treatment_5['@id']]})

    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            'biosample_ontology': liver['uuid']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'liver tissue male child (10 days) not treated and treated with ethanol'


def test_experiment_biosample_summary_3(testapp,
                                        base_experiment,
                                        biosample_22,
                                        biosample_23,
                                        library_1,
                                        library_2,
                                        treatment_5,
                                        replicate_1_1,
                                        replicate_2_1,
                                        epiblast,
                                        mouse):
    testapp.patch_json(biosample_22['@id'], {'model_organism_sex': 'male',
                                            'mouse_life_stage': 'embryonic',
                                            'organism': mouse['@id'],
                                            'treatments': [treatment_5['@id']]})

    testapp.patch_json(biosample_23['@id'], {'model_organism_sex': 'male',
                                            'mouse_life_stage': 'embryonic',
                                            'organism': mouse['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_22['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_23['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'epiblast cell not treated and treated with ethanol'


def test_experiment_biosample_summary_4(testapp,
                                        base_experiment,
                                        donor_1,
                                        donor_2,
                                        biosample_1,
                                        biosample_2,
                                        library_1,
                                        library_2,
                                        replicate_1_1,
                                        replicate_2_1,
                                        epidermis):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_1['@id'], {'sex': 'male'})
    testapp.patch_json(donor_2['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'biosample_ontology': epidermis['uuid'],
                                            'disease_term_id': ['DOID:2513']})

    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            'biosample_ontology': epidermis['uuid']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'skin epidermis tissue male child (10 days) with basal cell carcinoma and without disease'


def test_experiment_protein_tags(testapp, base_experiment, donor_1, donor_2, biosample_1, biosample_2, construct_genetic_modification, construct_genetic_modification_N, library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'], 'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'], 'genetic_modifications': [construct_genetic_modification_N['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    protein_tags = testapp.get(
        base_experiment['@id'] + '@@index-data'
    ).json['object']['protein_tags']
    assert len(protein_tags) == 2
    assert {
        'name': 'eGFP',
        'location': 'C-terminal',
        'target': '/targets/ATF4-human/'
    } in protein_tags
    assert {
        'name': 'eGFP',
        'location': 'N-terminal',
        'target': '/targets/ATF4-human/'
    } in protein_tags


def test_experiment_mint_chip_control(testapp, experiment_28):
    testapp.patch_json(experiment_28['@id'], {'control_type': 'input library'})
    res = testapp.get(experiment_28['@id'] + '@@index-data')
    assert res.json['object']['assay_title'] == 'Control Mint-ChIP-seq'
    testapp.patch_json(experiment_28['@id'], {'assay_term_name': 'eCLIP', 'control_type': 'mock input'})
    res = testapp.get(experiment_28['@id'] + '@@index-data')
    assert res.json['object']['assay_title'] == 'Control eCLIP'


def test_experiment_life_stage_age(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '25', 'life_stage': 'adult' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '25', 'life_stage': 'adult' })
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['life_stage_age'] == 'adult 25 years'
