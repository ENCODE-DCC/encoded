import pytest


@pytest.fixture
def base_reference(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/reference', item).json['@graph'][0]


@pytest.fixture
def upgrade_18_19_reference(testapp, lab, award, gene):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'examined_loci': [gene['@id']],
        'reference_type': 'functional elements'
    }
    return testapp.post_json('/reference', item).json['@graph'][0]

@pytest.fixture
def reference_19(base_reference):
    item = base_reference.copy()
    item.update({
        'internal_tags': ['RegulomeDB'],
        'schema_version': '19'
    })
    return item
