import pytest


def test_organism_upgrade_1_2(upgrader, human):
	human['ncbi_taxon_id'] = '9606'
	value = upgrader.upgrade('organism', human, current_version='1', target_version='2')
	assert value['schema_version'] == '2'
	assert value['taxon_id'] == 'NCBI:9606'
	assert 'ncbi_taxon_id' not in value


def test_organism_upgrade_2_3(upgrader, human):
	human['taxon_id'] = 'NCBI:9606'
	value = upgrader.upgrade('organism', human, current_version='2', target_version='3')
	assert value['schema_version'] == '3'
	assert value['taxon_id'] == 'NCBITaxon:9606'
