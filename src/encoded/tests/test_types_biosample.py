import pytest


def test_undefined_sex_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'unknown'


def test_undefined_sex_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'unknown'


def test_undefined_sex_mouse_with_model_organism_sex_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_sex': 'female'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'female'


def test_undefined_age_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == 'unknown'


def test_undefined_age_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == 'unknown'


def test_undefined_age_mouse_with_model_organism_age_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id'],
                                          'model_organism_age': '120',
                                          'model_organism_age_units': 'day'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == '120'


def test_undefined_age_units_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_undefined_age_units_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_undefined_age_units_mouse_with_model_organism_age_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id'],
                                          'model_organism_age': '120',
                                          'model_organism_age_units': 'day'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age_units'] == 'day'


def test_defined_life_stage_human(testapp, biosample, human, human_donor_1):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(human_donor_1['@id'], {'life_stage': 'embryonic'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor_1['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'embryonic'


def test_undefined_life_stage_human(testapp, biosample, human, human_donor_1):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'donor': human_donor_1['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'unknown'


def test_defined_life_stage_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'mouse_life_stage': 'adult'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'adult'


def test_undefined_life_stage_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'unknown'


def test_defined_health_status_human(testapp, biosample, human, human_donor_1):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(human_donor_1['@id'], {'health_status': 'healthy'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor_1['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['health_status'] == 'healthy'


def test_defined_health_status_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_health_status': 'sick'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['health_status'] == 'sick'


def test_undefined_health_status_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'health_status' not in res.json['object']


def test_biosample_summary(testapp,
                           donor_1,
                           biosample_1, treatment_5, liver):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10', 'sex': 'male', 'life_stage': 'child'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            "biosample_ontology": liver['uuid'],
                                            'disease_term_id': ['DOID:0080600'],
                                            "preservation_method": "cryopreservation",
                                            "post_nucleic_acid_delivery_time": 3,
                                            "post_nucleic_acid_delivery_time_units": "week",
                                            'pulse_chase_time': 2,
                                            'pulse_chase_time_units': 'hour',
                                            'treatments': [treatment_5['@id']]})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Homo sapiens male child (10 days) with COVID-19; liver tissue treated with ethanol,'
        ' 3 weeks post-nucleic acid delivery time, subjected to a 2 hour pulse-chase,'
        ' preserved by cryopreservation')


def test_biosample_summary_construct(testapp,
                                     fly,
                                     fly_donor,
                                     biosample_1,
                                     construct_genetic_modification,
                                     liver):

    testapp.patch_json(biosample_1['@id'], {
        'donor': fly_donor['@id'],
        'biosample_ontology': liver['uuid'],
        'genetic_modifications': [construct_genetic_modification['@id']],
        'model_organism_age': '10',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'organism': fly['@id']})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Drosophila melanogaster '
        'female (10 days) liver tissue stably expressing C-terminal eGFP-tagged ATF5 under daf-2 promoter')


def test_biosample_summary_construct_2(
    testapp,
    human,
    human_donor_1,
    biosample_1,
    liver
):
    testapp.patch_json(human_donor_1['@id'], {
        'age': '31',
        'age_units': 'year',
        'life_stage': 'adult',
        'sex': 'female'
        })
    testapp.patch_json(biosample_1['@id'], {
        'donor': human_donor_1['@id'],
        'biosample_ontology': liver['uuid'],
        'organism': human['@id'],
        'disease_term_id': ['DOID:0080600', 'DOID:9351']
        })
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Homo sapiens female adult (31 years) with COVID-19, diabetes mellitus; liver tissue')


def test_biosample_summary_construct_3(
    testapp,
    human,
    human_donor_1,
    biosample_1,
    liver,
    guides_transduction_GM,
    activation_genetic_modification
):
    testapp.patch_json(human_donor_1['@id'], {
        'age': '1',
        'age_units': 'month',
        'life_stage': 'child',
        'sex': 'female'
        })
    testapp.patch_json(biosample_1['@id'], {
        'donor': human_donor_1['@id'],
        'biosample_ontology': liver['uuid'],
        'organism': human['@id']
        })
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Homo sapiens female child (1 month) liver tissue')
    testapp.patch_json(biosample_1['@id'], {
        'genetic_modifications': [guides_transduction_GM['@id']]})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Homo sapiens female child (1 month) liver tissue genetically modified (insertion) using '
        'transduction (high MOI)')
    testapp.patch_json(guides_transduction_GM['@id'], {
        'guide_type': 'sgRNA'})
    testapp.patch_json(biosample_1['@id'], {
        'genetic_modifications': [guides_transduction_GM['@id'],
                                  activation_genetic_modification['@id']]})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Homo sapiens female child (1 month) liver tissue genetically modified (insertion) '
        'using transduction (high MOI), genetically modified using CRISPRa (sgRNA)')


def test_biosample_summary_construct_4(testapp,
                                     fly,
                                     fly_donor,
                                     biosample_1,
                                     construct_genetic_modification_N,
                                     liver):
    # Using GM with a target without genes
    testapp.patch_json(biosample_1['@id'], {
        'donor': fly_donor['@id'],
        'biosample_ontology': liver['uuid'],
        'genetic_modifications': [construct_genetic_modification_N['@id']],
        'model_organism_age': '10',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'organism': fly['@id']})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == (
        'Drosophila melanogaster '
        'female (10 days) liver tissue stably expressing N-terminal eGFP-tagged ATF4')


def test_simple_summary(testapp,
                           donor_1,
                           biosample_1, treatment_5, liver):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10', 'sex': 'male', 'life_stage': 'child'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            "biosample_ontology": liver['uuid'],
                                            'disease_term_id': ['DOID:0080600'],
                                            "preservation_method": "cryopreservation",
                                            "post_nucleic_acid_delivery_time": 3,
                                            "post_nucleic_acid_delivery_time_units": "week",
                                            'pulse_chase_time': 2,
                                            'pulse_chase_time_units': 'hour',
                                            'treatments': [treatment_5['@id']]})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['simple_summary'] == (
        'male child (10 days) with COVID-19; treated with ethanol')


def test_simple_summary_construct_strain(testapp,
                                     fly,
                                     fly_donor_strain,
                                     biosample_1,
                                     construct_genetic_modification,
                                     liver):

    testapp.patch_json(biosample_1['@id'], {
        'donor': fly_donor_strain['@id'],
        'biosample_ontology': liver['uuid'],
        'genetic_modifications': [construct_genetic_modification['@id']],
        'model_organism_age': '10',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'organism': fly['@id']})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['simple_summary'] == (
        'female (10 days) VK00033 stably expressing C-terminal eGFP-tagged ATF5 under daf-2 promoter')


def test_simple_summary_construct_2(
    testapp,
    human,
    human_donor_1,
    biosample_1,
    liver
):
    testapp.patch_json(human_donor_1['@id'], {
        'age': '31',
        'age_units': 'year',
        'life_stage': 'adult',
        'sex': 'female'
        })
    testapp.patch_json(biosample_1['@id'], {
        'donor': human_donor_1['@id'],
        'biosample_ontology': liver['uuid'],
        'organism': human['@id'],
        'disease_term_id': ['DOID:0080600', 'DOID:9351']
        })
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['simple_summary'] == (
        'female adult (31 years) with COVID-19, diabetes mellitus')


def test_simple_summary_construct_3(
    testapp,
    human,
    human_donor_1,
    biosample_1,
    liver
):
    testapp.patch_json(human_donor_1['@id'], {
        'age': '1',
        'age_units': 'month',
        'life_stage': 'child',
        'sex': 'female'
        })
    testapp.patch_json(biosample_1['@id'], {
        'donor': human_donor_1['@id'],
        'biosample_ontology': liver['uuid'],
        'organism': human['@id']
        })
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['simple_summary'] == (
        'female child (1 month)')


def test_perturbed_gm(
    testapp,
    biosample_1,
    interference_genetic_modification,
):
    testapp.patch_json(
        biosample_1['@id'],
        {
            'genetic_modifications': [interference_genetic_modification['@id']],
        }
    )
    res = testapp.get(biosample_1['@id'] + '@@index-data')
    assert res.json['object']['perturbed'] is True


def test_perturbed_treatment(
    testapp,
    biosample_1,
    treatment_not_perturbed,
    treatment_perturbed
):
    testapp.patch_json(
        biosample_1['@id'],
        {
            'treatments': [treatment_not_perturbed['@id']],
        }
    )
    res = testapp.get(biosample_1['@id'] + '@@index-data')
    assert res.json['object']['perturbed'] is False
    testapp.patch_json(
        biosample_1['@id'],
        {
            'treatments': [treatment_not_perturbed['@id'], treatment_perturbed['@id']],
        }
    )
    res = testapp.get(biosample_1['@id'] + '@@index-data')
    assert res.json['object']['perturbed'] is True


def test_perturbed_treatment_gm(
    testapp,
    biosample_1,
    interference_genetic_modification,
    treatment_5,
):
    testapp.patch_json(
        biosample_1['@id'],
        {
            'treatments': [treatment_5['@id']],
            'genetic_modifications': [interference_genetic_modification['@id']],
        }
    )
    res = testapp.get(biosample_1['@id'] + '@@index-data')
    assert res.json['object']['perturbed'] is True


def test_perturbed_none(
    testapp,
    biosample_1,
):
    res = testapp.get(biosample_1['@id'] + '@@index-data')
    assert res.json['object']['perturbed'] is False


def test_undefined_sample_collection_age(
    testapp,
    biosample,
    human,
    human_donor_1,
):
    testapp.patch_json(
        biosample['@id'],
        {'organism': human['@id'], 'donor': human_donor_1['@id']}
    )
    testapp.patch_json(
        human_donor_1['@id'],
        {'age': '30000', 'age_units': 'month', 'life_stage': 'embryonic'}
    )
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == '30000'
    assert res.json['object']['age_units'] == 'month'
    assert res.json['object']['age_display'] == '30000 months'
    testapp.patch_json(
        biosample['@id'],
        {
            'organism': human['@id'],
            'sample_collection_age': '90 or above',
            'sample_collection_age_units': 'year'
        }
    )
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == '90 or above'
    assert res.json['object']['age_units'] == 'year'
    assert res.json['object']['age_display'] == '90 or above years'


def test_origin_batch(testapp, biosample_part_of, biosample_cell_line, biosample_22, biosample_additional_a549):
    # Origin batch directly from part of biosample
    res = testapp.get(biosample_part_of['@id'] + '@@index-data')
    assert res.json['object']['origin_batch'] == biosample_cell_line['@id']
    # Different biosample type, defaults origin batch to the sample itself
    testapp.patch_json(
        biosample_part_of['@id'],
        {
            'part_of': biosample_22['uuid']
        }
    )
    res = testapp.get(biosample_part_of['@id'] + '@@index-data')
    assert res.json['object']['origin_batch'] == biosample_part_of['@id']
    # Part of biosample with another part of specified
    testapp.patch_json(
        biosample_cell_line['@id'],
        {
            'part_of': biosample_additional_a549['uuid']
        }
    )
    testapp.patch_json(
        biosample_part_of['@id'],
        {
            'part_of': biosample_cell_line['uuid']
        }
    )
    res = testapp.get(biosample_part_of['@id'] + '@@index-data')
    assert res.json['object']['origin_batch'] == biosample_additional_a549['@id']
