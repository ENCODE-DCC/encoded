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
