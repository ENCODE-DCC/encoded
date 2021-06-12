import pytest


def test_user_upgrade_1_2(upgrader, user_base):
	user_base['job_title'] = 'principal investigator'
	value = upgrader.upgrade('user', user_base, current_version='1', target_version='2')
	assert value['job_title'] == ['principal investigator']
	assert value['schema_version'] == '2'
