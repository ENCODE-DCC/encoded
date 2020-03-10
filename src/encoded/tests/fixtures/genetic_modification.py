import pytest
from ..constants import *


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
def genetic_modification_5(lab, award, crispr):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        'zygosity': 'homozygous',
        'treatments': [],
        'source': 'sigma',
        'product_id': '12345',
        'modification_techniques': [crispr],
        'modified_site': [{
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 5309435,
            'end': 5309451
            }]
    }

@pytest.fixture
def genetic_modification_6(lab, award, crispr, source):
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
def genetic_modification_7_invalid_reagent(lab, award, crispr):
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
def genetic_modification_7_valid_reagent(lab, award, crispr):
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
def genetic_modification_7_multiple_matched_identifiers(lab, award, crispr):
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
def genetic_modification_3(testapp, lab, award):
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
def genetic_modification_7_multiple_reagents(lab, award, crispr):
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
def gm_characterization(testapp, award, lab, construct_genetic_modification_N, attachment):
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]

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
def recomb_tag_1(testapp, lab, award, target, treatment, document):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'site-specific recombination',
        'modified_site_by_target_id': target['@id'],
        'modified_site_nonspecific': 'random',
        'category': 'insertion',
        'treatments': [treatment['@id']],
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

