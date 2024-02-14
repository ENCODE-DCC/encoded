import pytest


@pytest.fixture
def ontology():
    ontology = {
        'UBERON:0002469': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:0001096',
                'UBERON:1111111'
            ]
        },
        'UBERON:1111111': {
            'part_of': []
        },
        'UBERON:0001096': {
            'part_of': []
        },
        'UBERON:0001043': {
            'part_of': [
                'UBERON:0001007',
                'UBERON:0004908'
            ]
        },
        'UBERON:0001007': {
            'part_of': []
        },
        'UBERON:0004908': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:1234567'
            ]
        },
        'UBERON:1234567': {
            'part_of': [
                'UBERON:0006920'
            ]
        },
        'UBERON:0006920': {
            'part_of': []
        },
        'UBERON:1231231': {
            'name': 'liver'
        }
    }
    return ontology
