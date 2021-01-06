import pytest


@pytest.fixture
def tissue_base(testapp, human_postnatal_donor_base, heart_ontology):
    item = {
        'biosample_ontology': heart_ontology['uuid'],
        'derivation_process': ['dissection'],
        'derived_from': [human_postnatal_donor_base['uuid']]
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]

