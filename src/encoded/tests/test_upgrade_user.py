import pytest


def test_user_upgrade_1_2(upgrader, user_base):
	user_base['job_title'] = 'principal investigator'
	value = upgrader.upgrade('user', user_base, current_version='1', target_version='2')
	assert value['job_title'] == ['principal investigator']
	assert value['schema_version'] == '2'


def test_user_upgrade_2_3(upgrader, user_base):
	user_base['job_title'] = ['principal investigator']
	value = upgrader.upgrade('user', user_base, current_version='2', target_version='3')
	assert value['job_title'] == 'principal investigator'
	assert value['schema_version'] == '3'
