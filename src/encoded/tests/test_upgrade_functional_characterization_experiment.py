import pytest


def test_functional_characterization_experiment_upgrade_2_to_3(upgrader, pce_fcc_experiment):
    value = upgrader.upgrade('functional_characterization_experiment', pce_fcc_experiment, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['plasmids_library_type'] == 'other' 


def test_functional_characterization_experiment_upgrade_4_to_5(upgrader, pce_fcc_experiment_2):
    value = upgrader.upgrade('functional_characterization_experiment', pce_fcc_experiment_2, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert value['biosample_ontology'] == '09e6c39a-92af-41fc-a535-7a86d5e9590a'


def test_functional_characterization_experiment_upgrade_5_to_6(upgrader, pce_fcc_other_experiment):
    value = upgrader.upgrade('functional_characterization_experiment', pce_fcc_other_experiment, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['plasmids_library_type'] == 'elements cloning'
    assert value['notes'] == 'The plasmids_library_type of this pooled clone sequencing experiment needs to be checked as it was automatically upgraded by ENCD-5303.'


def test_functional_characterization_experiment_upgrade_7_to_8(upgrader, functional_characterization_experiment_7):
    value = upgrader.upgrade('functional_characterization_experiment', functional_characterization_experiment_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert value['examined_loci'][0]['expression_measurement_method'] == 'HCR-FlowFISH'


def test_functional_characterization_experiment_upgrade_8_to_9(upgrader, fcc_experiment_elements_mapping, pooled_clone_sequencing):
    value = upgrader.upgrade('functional_characterization_experiment', fcc_experiment_elements_mapping, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert isinstance(value['elements_mappings'], list)
    assert 'elements_mapping' not in value
    assert value['elements_mappings'] == [pooled_clone_sequencing['uuid']]
