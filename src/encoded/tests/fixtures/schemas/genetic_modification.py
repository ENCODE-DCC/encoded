import pytest


@pytest.fixture
def genetic_modification(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'CRISPR',
        'zygosity': 'homozygous'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_RNAi(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'RNAi'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_source(testapp, lab, award, source, gene):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'introduced_gene': gene['@id'],
        'purpose': 'expression',
        'method': 'CRISPR',
        'reagents': [
            {
                'source': source['@id'],
                'identifier': 'sigma:ABC123'
            }
        ]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def crispr_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'CRISPR'
    }


@pytest.fixture
def crispr_deletion_1(testapp, lab, award, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'CRISPR',
        'modified_site_by_target_id': target['@id'],
        'guide_rna_sequences': ['ACCGGAGA']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]



@pytest.fixture
def tale_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'TALEN',
        'zygosity': 'heterozygous'
    }


@pytest.fixture
def crispr_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'CRISPR'
    }


@pytest.fixture
def bombardment_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'bombardment'
    }


@pytest.fixture
def recomb_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'site-specific recombination'
    }


@pytest.fixture
def transfection_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection'
    }


@pytest.fixture
def crispri(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'CRISPR'
    }


@pytest.fixture
def rnai(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi'
    }


@pytest.fixture
def mutagen(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'mutagenesis',
        'purpose': 'repression',
        'method': 'mutagen treatment'
    }


@pytest.fixture
def tale_replacement(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'replacement',
        'purpose': 'characterization',
        'method': 'TALEN',
        'zygosity': 'heterozygous'
    }

@pytest.fixture
def mpra(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'transduction'
    }


@pytest.fixture
def starr_seq(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'episome',
        'purpose': 'characterization',
        'method': 'transient transfection'
    }


@pytest.fixture
def introduced_elements(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'episome',
        'purpose': 'characterization',
        'method': 'transient transfection',
        'introduced_elements': 'genomic DNA regions'
    }

@pytest.fixture
def crispr_tag_1(testapp, lab, award, ctcf):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'CRISPR',
        'modified_site_by_gene_id': ctcf['@id'],
        'introduced_tags': [{'name': 'mAID-mClover', 'location': 'C-terminal'}]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def mpra_1(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'transduction',
        'introduced_elements': 'synthesized DNA',
        'modified_site_nonspecific': 'random'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def recomb_tag_1(testapp, lab, award, target, treatment_5, document):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'site-specific recombination',
        'modified_site_by_target_id': target['@id'],
        'modified_site_nonspecific': 'random',
        'category': 'insertion',
        'treatments': [treatment_5['@id']],
        'documents': [document['@id']],
        'introduced_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def rnai_1(testapp, lab, award, source, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi',
        'reagents': [{'source': source['@id'], 'identifier': 'addgene:12345'}],
        'rnai_sequences': ['ATTACG'],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_1(lab, award):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'modifiction_description': 'some description'
    }


@pytest.fixture
def genetic_modification_2(lab, award):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'modification_description': 'some description',
        'modification_zygocity': 'homozygous',
        'modification_purpose': 'tagging',
        'modification_treatments': [],
        'modification_genome_coordinates': [{
            'chromosome': '11',
            'start': 5309435,
            'end': 5309451
            }]
    }


@pytest.fixture
def crispr_gm(lab, award, source):
    return {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'source': source['uuid'],
        'guide_rna_sequences': [
            "ACA",
            "GCG"
        ],
        'insert_sequence': 'TCGA',
        'aliases': ['encode:crispr_technique1'],
        '@type': ['Crispr', 'ModificationTechnique', 'Item'],
        '@id': '/crisprs/79c1ec08-c878-4419-8dba-66aa4eca156b/',
        'uuid': '79c1ec08-c878-4419-8dba-66aa4eca156b'
    }


@pytest.fixture
def genetic_modification_5(lab, award, crispr_gm):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        'zygosity': 'homozygous',
        'treatments': [],
        'source': 'sigma',
        'product_id': '12345',
        'modification_techniques': [crispr_gm],
        'modified_site': [{
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 5309435,
            'end': 5309451
            }]
    }


@pytest.fixture
def genetic_modification_6(lab, award, crispr_gm, source):
    return {
        'purpose': 'validation',
        'category': 'deeltion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "placeholder_id",
                "source": source['uuid']
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_invalid_reagent(lab, award, crispr_gm):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "placeholder_id",
                "source": "/sources/sigma/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_valid_reagent(lab, award, crispr_gm):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "ABC123",
                "source": "/sources/sigma/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_addgene_source(testapp):
    item = {
        'name': 'addgene',
        'title': 'Addgene',
        'status': 'released'
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_7_multiple_matched_identifiers(lab, award, crispr_gm):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "12345",
                "source": "/sources/addgene/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_multiple_reagents(lab, award, crispr_gm):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "12345",
                "source": "/sources/addgene/",
                "url": "http://www.addgene.org"
            },
            {
                "identifier": "67890",
                "source": "/sources/addgene/",
                "url": "http://www.addgene.org"
            }
        ]
    }


@pytest.fixture
def genetic_modification_8(lab, award):
    return {
        'purpose': 'analysis',
        'category': 'interference',
        'award': award['uuid'],
        'lab': lab['uuid'],
        "method": "CRISPR",
    }


@pytest.fixture
def construct_genetic_modification(
        testapp,
        lab,
        award,
        document,
        target,
        target_promoter):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection',
        'introduced_tags': [{'name':'eGFP', 'location': 'C-terminal', 'promoter_used': target_promoter['@id']}],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def construct_genetic_modification_N(
        testapp,
        lab,
        award,
        document,
        target):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection',
        'introduced_tags': [{'name':'eGFP', 'location': 'N-terminal'}],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def interference_genetic_modification(
        testapp,
        lab,
        award,
        document,
        target):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi',        
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def crispr_knockout(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'knockout',
        'purpose': 'characterization',
        'method': 'CRISPR'
    }


@pytest.fixture
def recombination_knockout(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'knockout',
        'purpose': 'repression',
        'method': 'site-specific recombination',
        'modified_site_by_coordinates': {
            "assembly": "GRCh38",
            "chromosome": "11",
            "start": 60000,
            "end": 62000
        }
    }


@pytest.fixture
def characterization_insertion_transfection(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'stable transfection',
        'modified_site_nonspecific': 'random',
        'introduced_elements': 'synthesized DNA'
    }


@pytest.fixture
def characterization_insertion_CRISPR(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'CRISPR',
        'modified_site_nonspecific': 'random',
        'introduced_elements': 'synthesized DNA'
    }


@pytest.fixture
def disruption_genetic_modification(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'disruption',
        'purpose': 'characterization',
        'method': 'CRISPR'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def activation_genetic_modification(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'activation',
        'purpose': 'characterization',
        'method': 'CRISPR'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def HR_knockout(lab, award, target):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'knockout',
        'purpose': 'repression',
        'method': 'homologous recombination',
        'modified_site_by_target_id': target['@id']
    }


@pytest.fixture
def CRISPR_introduction(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'expression',
        'method': 'transient transfection'
    }
