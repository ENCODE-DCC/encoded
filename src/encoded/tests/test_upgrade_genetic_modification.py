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
