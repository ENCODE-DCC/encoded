import pytest


def test_functional_characterization_experiment_upgrade_2_to_3(upgrader, pce_fcc_experiment):
    value = upgrader.upgrade('functional_characterization_experiment', pce_fcc_experiment, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['plasmids_library_type'] == 'other' 
