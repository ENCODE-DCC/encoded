import pytest


def test_publication_upgrade_1_2(upgrader, publication_base):
	publication_base['identifiers'] = ['doi:10.1101/2020.06.25.171793', 'PMID:234523']
	value = upgrader.upgrade('publication', publication_base, current_version='1', target_version='2')
	assert 'identifiers' not in value
	assert value['schema_version'] == '2'
	assert value['doi'] == '10.1101/2020.06.25.171793'
	assert value['pmid'] == '234523'
