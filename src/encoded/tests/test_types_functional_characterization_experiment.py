import pytest


def test_fcc_replicate_type(
    testapp, functional_characterization_experiment, pooled_clone_sequencing
):
    res = testapp.get(
        functional_characterization_experiment['@id']+'@@index-data'
    )
    assert res.json['object']['replication_type'] == 'unreplicated'
    res = testapp.get(
        pooled_clone_sequencing['@id']+'@@index-data'
    )
    assert 'replication_type' not in res.json['object']


def test_fcc_crispr_assay_perturbation(testapp, functional_characterization_experiment_disruption_screen, biosample_1, biosample_2, library_1, library_2, replicate_1_fce, replicate_2_fce, disruption_genetic_modification, activation_genetic_modification, binding_genetic_modification, ctcf):
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [disruption_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [disruption_genetic_modification['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_fce['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_fce['@id'], {'library': library_2['@id']})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert res.json['object']['perturbation_type'] == 'disruption'
    # more than one CRISPR characterization genetic modification
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [disruption_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [disruption_genetic_modification['@id'], activation_genetic_modification['@id']]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert 'perturbation_type' not in res.json['object']
    # binding CRISPR genetic modification
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [binding_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [binding_genetic_modification['@id']]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert 'perturbation_type' not in res.json['object']


def test_fcc_crispr_assay_readout_method(testapp, functional_characterization_experiment_disruption_screen, biosample_1, biosample_2, library_1, library_2, replicate_1_fce, replicate_2_fce, disruption_genetic_modification, activation_genetic_modification, binding_genetic_modification, ctcf):
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [disruption_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [disruption_genetic_modification['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_fce['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_fce['@id'], {'library': library_2['@id']})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert res.json['object']['crispr_screen_readout'] == 'proliferation'
    # patch with basic examined_loci, no method
    testapp.patch_json(functional_characterization_experiment_disruption_screen['@id'], {'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 100}]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert 'crispr_screen_readout' not in res.json['object']
    # expression_measurement_method in examined_loci
    testapp.patch_json(functional_characterization_experiment_disruption_screen['@id'], {'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 100, 'expression_measurement_method': 'HCR-FlowFISH'}]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert res.json['object']['crispr_screen_readout'] == 'HCR-FlowFISH'
    # multiple different expression_measurement_method in examined_loci
    testapp.patch_json(
        functional_characterization_experiment_disruption_screen['@id'],
        {'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 100, 'expression_measurement_method': 'HCR-FlowFISH'}, 
        {'gene': ctcf['uuid'], 'expression_percentile': 10, 'expression_measurement_method': 'PrimeFlow'}]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id']+'@@index-data')
    assert 'crispr_screen_readout' not in res.json['object']
