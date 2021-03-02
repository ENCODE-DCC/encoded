import pytest


def test_tissue_upgrade_1_2(upgrader, tissue_base):
	tissue_base['url'] = 'https://www.protocols.io/'
	value = upgrader.upgrade('tissue', tissue_base, current_version='1', target_version='2')
	assert 'url' not in value
	assert value['urls'] == ['https://www.protocols.io/']
	assert value['schema_version'] == '2'
