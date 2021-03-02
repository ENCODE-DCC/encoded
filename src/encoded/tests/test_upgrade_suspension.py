import pytest


def test_suspension_upgrade_1_2(upgrader, suspension_base):
	suspension_base['biosample_ontology'] = 'UBERON_0002113'
	value = upgrader.upgrade('suspension', suspension_base, current_version='1', target_version='2')
	assert 'biosample_ontology' not in value
	assert value['schema_version'] == '2'

def test_suspension_upgrade_2_3(upgrader, suspension_base):
	suspension_base['url'] = 'https://www.protocols.io/'
	value = upgrader.upgrade('suspension', suspension_base, current_version='2', target_version='3')
	assert 'url' not in value
	assert value['urls'] == ['https://www.protocols.io/']
	assert value['schema_version'] == '3'
