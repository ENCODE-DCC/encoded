import pytest


def test_dataset_upgrade_1_2(upgrader, dataset_base):
	dataset_base['corresponding_contributor'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('dataset', dataset_base, current_version='1', target_version='2')
	assert 'corresponding_contributor' not in value
	assert value['corresponding_contributors'] == ['62ba2fba-8ee9-4996-b804-f9a673d137c3']
	assert value['schema_version'] == '2'
