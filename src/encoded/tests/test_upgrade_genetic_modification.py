import pytest


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
def crispr(lab, award, source):
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
        '@id': '/crisprs/d16821e3-a8b6-40a5-835c-355c619a9011/',
        'uuid': 'd16821e3-a8b6-40a5-835c-355c619a9011'
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


def test_genetic_modification_upgrade_1_2(upgrader, genetic_modification_1):
    value = upgrader.upgrade('genetic_modification', genetic_modification_1,
                             current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert value.get('modification_description') == 'some description'


def test_genetic_modification_upgrade_2_3(upgrader, genetic_modification_2):
    value = upgrader.upgrade('genetic_modification', genetic_modification_2,
                             current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value.get('description') == 'some description'
    assert value.get('zygosity') == 'homozygous'
    assert value.get('purpose') == 'tagging'
    assert 'modification_genome_coordinates' not in value
    assert 'modification_treatments' not in value


'''
def test_genetic_modification_upgrade_5_6(upgrader, genetic_modification_5, crispr):
    value = upgrader.upgrade('genetic_modification', genetic_modification_5,
                             current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert 'modification_techniques' not in value
    assert value['modification_technique'] == 'CRISPR'
    assert 'modified_site' not in value
    assert 'target' not in value
    assert 'purpose' in value
    assert value['purpose'] == 'analysis'
    assert len(value['guide_rna_sequences']) == 2
    assert value['aliases'][0] == 'encode:crispr_technique1-CRISPR'
    assert value['introduced_sequence'] == 'TCGA'
    assert 'reagent_availability' in value
    assert value['reagent_availability']['repository'] == 'sigma'
    assert value['reagent_availability']['identifier'] == '12345'
'''
