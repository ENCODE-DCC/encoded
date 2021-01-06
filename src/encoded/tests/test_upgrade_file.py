import pytest


def test_raw_sequence_file_upgrade_1_2(upgrader, raw_sequence_file_base):
	raw_sequence_file_base['award'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('raw_sequence_file', raw_sequence_file_base, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert 'award' not in value
	assert isinstance(value['derived_from'], str)


def test_reference_file_upgrade_1_2(upgrader, reference_file_base):
	dummy_fileset = {'description': 'group of ref files'}
	reference_file_base['fileset'] = dummy_fileset
	value = upgrader.upgrade('reference_file', reference_file_base, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert 'fileset' not in value
