import pytest
from encoded.tests.fixtures.schemas.analysis import analysis_1
from snovault import load_schema


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
        'skin epidermis tissue male child (10 days) with basal cell carcinoma; and without disease'


def test_experiment_biosample_summary_5(testapp,
                                        base_experiment,
                                        mouse_donor_1_1,
                                        mouse_donor_2_1,
                                        base_mouse_biosample,
                                        base_mouse_biosample_2,
                                        library_1,
                                        library_2,
                                        treatment_5,
                                        replicate_1_1,
                                        replicate_2_1,
                                        heart):
    testapp.patch_json(mouse_donor_1_1['@id'], {'strain_name': 'B6NCrl', 'strain_background': 'C57BL/6'})
    testapp.patch_json(mouse_donor_2_1['@id'], {'strain_name': 'B6NCrl', 'strain_background': 'C57BL/6'})
    testapp.patch_json(base_mouse_biosample['@id'], {'donor': mouse_donor_1_1['@id'],
                                            'biosample_ontology': heart['uuid'],
                                            'model_organism_sex': 'mixed',
                                            'model_organism_age': '11.5',
                                            'model_organism_age_units': 'day',
                                            'treatments': [treatment_5['@id']]})

    testapp.patch_json(base_mouse_biosample_2['@id'], {'donor': mouse_donor_2_1['@id'],
                                            'biosample_ontology': heart['uuid'],
                                            'model_organism_sex': 'mixed',
                                            'model_organism_age': '11.5',
                                            'model_organism_age_units': 'day'})

    testapp.patch_json(library_1['@id'], {'biosample': base_mouse_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_mouse_biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'strain B6NCrl heart tissue (11.5 days) not treated and treated with ethanol'


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
        'target': '/targets/ATF5-human/'
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

def test_experiment_default_analysis(
    testapp,
    dummy_request,
    base_experiment,
    analysis_1,
    analysis_2,
    file_bam_1_1,
    file_bam_2_1,
    analysis_step_run_chip_encode4,
    pipeline_chip_encode4,
    analysis_step_run_dnase_encode4,
    pipeline_dnase_encode4,
    encode_lab,
    encode4_award,
    ENCODE3_award,
):
    # Guard relevant schema enum orders
    status_order = list(dummy_request.registry['types']['analysis'].schema['properties']['status']['enum'])
    assert status_order == [
        'in progress',
        'released',
        'archived',
        'deleted',
        'revoked',
    ]
    award_rfa_order = list(dummy_request.registry['types']['award'].schema['properties']['rfa']['enum'])
    assert award_rfa_order == [
        'ENCODE4',
        'ENCODE3',
        'ENCODE2',
        'ENCODE2-Mouse',
        'ENCODE',
        'GGR',
        'ENCORE',
        'Roadmap',
        'modENCODE',
        'modERN',
        'community'
    ]
    assembly_order = list(dummy_request.registry['types']['file'].schema['properties']['assembly']['enum'])
    assert assembly_order == [
        'GRCh38',
        'GRCh38-minimal',
        'hg19',
        'ENC001.1',
        'ENC002.1',
        'ENC003.1',
        'ENC004.1',
        'GRCm39',
        'mm10',
        'mm10-minimal',
        'mm9',
        'dm6',
        'dm3',
        'ce11',
        'ce10',
        'J02459.1',
    ]
    genome_annotation_order = list(dummy_request.registry['types']['file'].schema['properties']['genome_annotation']['enum'])
    assert genome_annotation_order == [
        'V33',
        'V30',
        'V29',
        'V24',
        'V22',
        'V19',
        'V10',
        'V7',
        'V3c',
        'miRBase V21',
        'M26',
        'M21',
        'M14',
        'M7',
        'M4',
        'M3',
        'M2',
        'ENSEMBL V65',
        'WS245',
        'WS235',
        'None',
    ]

    testapp.patch_json(
        analysis_1['@id'],
        {'status': 'in progress', 'files': [file_bam_1_1['@id']]}
    )
    testapp.patch_json(
        analysis_2['@id'],
        {'status': 'in progress', 'files': [file_bam_2_1['@id']]}
    )
    testapp.patch_json(
        base_experiment['@id'],
        {
            'analyses': [analysis_1['@id'], analysis_2['@id']],
            'status': 'in progress'
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    # Date-time makes the decision here
    assert res.json['object']['default_analysis'] == analysis_2['@id']

    # Released experiment with only in progress analyses
    testapp.patch_json(
        base_experiment['@id'],
        {'status': 'released', 'date_released': '2021-03-31'}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert 'default_analysis' not in res.json['object']

    # Having annotation is better than no annotation
    testapp.patch_json(analysis_1['@id'], {'status': 'released'})
    testapp.patch_json(analysis_2['@id'], {'status': 'released'})
    testapp.patch_json(file_bam_1_1['@id'], {'genome_annotation': 'M21'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert res.json['object']['default_analysis'] == analysis_1['@id']

    # Assembly is more important than annotation
    testapp.patch_json(file_bam_1_1['@id'], {'assembly': 'mm9'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert res.json['object']['default_analysis'] == analysis_2['@id']

    # ENCODE uniform processing > lab processing before RFA
    testapp.patch_json(
        file_bam_1_1['@id'],
        {'step_run': analysis_step_run_chip_encode4['@id']}
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {'step_run': analysis_step_run_dnase_encode4['@id']}
    )
    testapp.patch_json(pipeline_chip_encode4['@id'], {'lab': encode_lab['@id']})
    testapp.patch_json(
        pipeline_dnase_encode4['@id'], {'award': encode4_award['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert res.json['object']['default_analysis'] == analysis_1['@id']

    # Pipeline award RFA rank
    testapp.patch_json(
        pipeline_dnase_encode4['@id'], {'lab': encode_lab['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert res.json['object']['default_analysis'] == analysis_2['@id']

    # Released > archived
    testapp.patch_json(analysis_2['@id'], {'status': 'archived'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')

    analysis_1_audits = testapp.get(analysis_1['@id'] + '@@index-data').json['audit']
    analysis_2_audits = testapp.get(analysis_2['@id'] + '@@index-data').json['audit']
    experiment_audits = res.json['audit']

    for audit_type in analysis_1_audits:
        for audit_instance in analysis_1_audits[audit_type]:
            audit_detail = audit_instance['detail']
            assert any(experiment_audit['detail'] == audit_detail
               for experiment_audit in experiment_audits.get(audit_type))

    for audit_type in analysis_2_audits:
        for audit_instance in analysis_2_audits[audit_type]:
            audit_detail = audit_instance['detail']
            assert all(experiment_audit['detail'] != audit_detail
               for experiment_audit in experiment_audits.get(audit_type))
 
    assert res.json['object']['default_analysis'] == analysis_1['@id']

    # Rfa is working for different versions of pipeline
    testapp.patch_json(analysis_1['@id'], {'status': 'archived'})
    testapp.patch_json(analysis_2['@id'], {"pipeline_version": "1.6.1"})
    testapp.patch_json(
        pipeline_dnase_encode4['@id'], {'award': encode4_award['@id']}
    )
    testapp.patch_json(
        pipeline_chip_encode4['@id'], {'award': ENCODE3_award['@id']}
    )
    testapp.patch_json(file_bam_1_1['@id'], {'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'genome_annotation': 'M21'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')


    analysis_1_audits = testapp.get(analysis_1['@id'] + '@@index-data').json['audit']
    analysis_2_audits = testapp.get(analysis_2['@id'] + '@@index-data').json['audit']
    experiment_audits = res.json['audit']

    for audit_type in analysis_1_audits:
        for audit_instance in analysis_1_audits[audit_type]:
            audit_detail = audit_instance['detail']
            assert all(experiment_audit['detail'] != audit_detail
               for experiment_audit in experiment_audits.get(audit_type))

    for audit_type in analysis_2_audits:
        for audit_instance in analysis_2_audits[audit_type]:
            audit_detail = audit_instance['detail']
            assert any(experiment_audit['detail'] == audit_detail
               for experiment_audit in experiment_audits.get(audit_type))

    assert res.json['object']['default_analysis'] == analysis_2['@id']


def test_experiment_replication_count_0(testapp, base_experiment):
    res = testapp.get(base_experiment['@id'] + '@@index-data') 
    assert res.json['object']['bio_replicate_count'] == 0 and res.json['object']['tech_replicate_count'] == 0


def test_experiment_replication_count_2(testapp, base_experiment, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data') 
    assert res.json['object']['bio_replicate_count'] == 2 and res.json['object']['tech_replicate_count'] == 2
