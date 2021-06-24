import pytest


def test_sequencing_run_upgrade_1_2(upgrader, sequencing_run_base):
	sequencing_run_base['derived_from'] = 'LATLB234DEF'
	value = upgrader.upgrade('sequencing_run', sequencing_run_base, current_version='1', target_version='2')
	assert value['derived_from'] == ['LATLB234DEF']
	assert value['schema_version'] == '2'


def test_sequencing_run_upgrade_2_3(upgrader, sequencing_run_base):
	sequencing_run_base['flowcell_details'] = {"machine":"A00437","lane":"4","flowcell":"HH22VDSXX"}
	value = upgrader.upgrade('sequencing_run', sequencing_run_base, current_version='2', target_version='3')
	assert 'flowcell_details' not in value
	assert value['schema_version'] == '3'
