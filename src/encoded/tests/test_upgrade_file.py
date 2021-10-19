import pytest


def test_file_upgrade_1_2(upgrader, raw_sequence_file_base):
	raw_sequence_file_base['award'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('raw_sequence_file', raw_sequence_file_base, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert 'award' not in value


def test_processed_matrix_file_upgrade_4_5(upgrader, processed_matrix_file_base):
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='4', target_version='5')
	assert value['schema_version'] == '5'
	assert value['layers'][0]['is_primary_data'] == True


def test_processed_matrix_file_upgrade_5_6(upgrader, processed_matrix_file_base):
	del processed_matrix_file_base['is_primary_data']
	value = upgrader.upgrade('processed_matrix_file', processed_matrix_file_base, current_version='5', target_version='6')
	assert value['schema_version'] == '6'
	assert value['is_primary_data'] == False
