import pytest


@pytest.fixture
def crispr_deletion(testapp, lab, award, target):
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
def crispr_tag(testapp, lab, award, ctcf):
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
def mpra(testapp, lab, award):
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
def recomb_tag(testapp, lab, award, target, treatment, document):
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
def rnai(testapp, lab, award, source, target):
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


def test_perturbation_flag(testapp, crispr_deletion, rnai, mpra, recomb_tag, crispr_tag):
    res = testapp.get(crispr_deletion['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(rnai['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(mpra['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(recomb_tag['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == False
    res = testapp.get(crispr_tag['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == False