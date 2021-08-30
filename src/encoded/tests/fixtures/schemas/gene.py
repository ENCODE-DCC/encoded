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


@pytest.fixture
def gene(ctcf):
    return ctcf


@pytest.fixture
def bap1(testapp, organism):
    item = {
        'uuid': '91205c22-2748-47e1-b261-8c38236f4e98',
        'dbxrefs': ['HGNC:950'],
        'geneid': '8314',
        'symbol': 'BAP1',
        'ncbi_entrez_status': 'live',
        'organism': organism['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def ctcf(testapp, organism):
    item = {
        'uuid': 'a9288b44-6ef4-460e-a3d6-464fd625b103',
        'dbxrefs': ['HGNC:13723'],
        'geneid': '10664',
        'symbol': 'CTCF',
        'ncbi_entrez_status': 'live',
        'organism': organism['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def myc(testapp, human):
    item = {
        'uuid': 'd358f63b-63d6-408f-baca-13881c6c79a1',
        'dbxrefs': ['HGNC:7553'],
        'geneid': '4609',
        'symbol': 'MYC',
        'ncbi_entrez_status': 'live',
        'organism': human['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def tbp(testapp, mouse):
    item = {
        'uuid': '93def54f-d998-4d85-ba9d-e985d4f736da',
        'dbxrefs': ['MGI:101838'],
        'geneid': '21374',
        'symbol': 'Tbp',
        'ncbi_entrez_status': 'live',
        'organism': mouse['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def gene_1(gene):
    item = gene.copy()
    item.update({
        'go_annotations': [
            {
                "go_id": "GO:0000122",
                "go_name": "negative regulation of transcription by RNA polymerase II",
                "go_evidence_code": "IDA",
                "go_aspect": "P"
            },
            {
                "go_id": "GO:0000775",
                "go_name": "chromosome, centromeric region",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
            {
                "go_id": "GO:0000793",
                "go_name": "condensed chromosome",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
        ],
    })
    return item


@pytest.fixture
def atf5(testapp, human):
    item = {
        'uuid': '82397002-0f6b-4a7c-832b-40be5a27ad9b',
        'dbxrefs': ['HGNC:790'],
        'geneid': '22809',
        'symbol': 'ATF5',
        'ncbi_entrez_status': 'live',
        'organism': human['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]
