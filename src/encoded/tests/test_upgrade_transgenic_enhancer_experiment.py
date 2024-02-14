import pytest


def test_transgenic_enhancer_experiment_upgrade_1_to_2(upgrader, transgenic_enhancer_experiment):
    value = upgrader.upgrade('transgenic_enhancer_experiment', transgenic_enhancer_experiment, current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert value['assay_term_name'] == 'enhancer reporter assay' 
