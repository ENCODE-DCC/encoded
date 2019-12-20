import pytest


@pytest.fixture
def gene_locations_wrong_assembly(testapp, human):
    item = {
        'uuid': 'd358f63b-63d6-408f-baca-13881c6c79a1',
        'dbxrefs': ['HGNC:7553'],
        'geneid': '4609',
        'symbol': 'MYC',
        'ncbi_entrez_status': 'live',
        'organism': human['uuid'],
        'locations': [{'assembly': 'mm10', 'chromosome': 'chr18', 'start': 47808713, 'end': 47814692}]
    }
    return item


def test_gene_assembly_locations(testapp, gene_locations_wrong_assembly):
    testapp.post_json('/gene', gene_locations_wrong_assembly, status=422)
    gene_locations_wrong_assembly.update({'locations': [{'assembly': 'hg19', 'chromosome': 'chr18', 'start': 47808713, 'end': 47814692}]})
    testapp.post_json('/gene', gene_locations_wrong_assembly, status =201)
