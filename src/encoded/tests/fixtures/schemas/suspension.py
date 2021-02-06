import pytest


@pytest.fixture
def suspension_base(testapp, heart_ontology, tissue_base):
    item = {
        'derivation_process': ['mechanical dissociation'],
        'suspension_type': 'cell',
        'derived_from': [tissue_base['uuid']]
    }
    return testapp.post_json('/suspension', item, status=201).json['@graph'][0]
