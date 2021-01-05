import pytest


def test_library_upgrade_1_2(upgrader, library_base):
	library_base['award'] = '62ba2fba-8ee9-4996-b804-f9a673d137c3'
	value = upgrader.upgrade('library', library_base, current_version='1', target_version='2')
	assert 'award' not in value
	assert value['schema_version'] == '2'
