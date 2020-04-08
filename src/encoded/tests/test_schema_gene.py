import pytest


def test_gene_assembly_locations(testapp, gene_locations_wrong_assembly):
    testapp.post_json('/gene', gene_locations_wrong_assembly, status=422)
    gene_locations_wrong_assembly.update({'locations': [{'assembly': 'hg19', 'chromosome': 'chr18', 'start': 47808713, 'end': 47814692}]})
    testapp.post_json('/gene', gene_locations_wrong_assembly, status =201)
