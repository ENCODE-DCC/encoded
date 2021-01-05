import pytest


def test_raw_sequence_file_upgrade_1_2(upgrader, raw_sequence_file_base):
	raw_sequence_file_base['award'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('raw_sequence_file', raw_sequence_file_base, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert 'award' not in value
	assert isinstance(value['derived_from'], str)
