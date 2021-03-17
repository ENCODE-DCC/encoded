import pytest


def test_sequencing_run_upgrade_1_2(upgrader, sequencing_run_base):
	sequencing_run_base['derived_from'] = 'LATLB234DEF'
	value = upgrader.upgrade('sequencing_run', sequencing_run_base, current_version='1', target_version='2')
	assert value['derived_from'] == ['LATLB234DEF']
	assert value['schema_version'] == '2'
