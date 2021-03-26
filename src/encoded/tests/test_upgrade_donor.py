import pytest


def test_human_postnatal_donor_upgrade_1_2(upgrader, human_postnatal_donor_base):
	human_postnatal_donor_base['family_history_breast_cancer'] = ['sister', 'mother']
	value = upgrader.upgrade('human_postnatal_donor', human_postnatal_donor_base, current_version='1', target_version='2')
	assert value['family_members_history_breast_cancer'] == ['sister', 'mother']
	assert 'family_history_breast_cancer' not in value
	assert value['schema_version'] == '2'
