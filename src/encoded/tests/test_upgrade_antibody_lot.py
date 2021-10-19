import pytest


def test_antibody_lot_upgrade_1_2(upgrader, antibody_lot_base):
	antibody_lot_base['target'] = 'target_base'
	value = upgrader.upgrade('antibody_lot', antibody_lot_base, current_version='1', target_version='2')
	assert 'target' not in value
	assert value['targets'] == ['target_base']
	assert value['schema_version'] == '2'
