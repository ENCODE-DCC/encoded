import pytest


@pytest.fixture
def base_chipmunk(testapp):
    item = {
        'name': 'chimpmunk',
        'ncbi_taxon_id': '12345',
        'scientific_name': 'Chip chipmunicus'
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


@pytest.fixture
def organism(human):
    return human


@pytest.fixture
def worm(testapp):
    item = {
        'uuid': '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20',
        'name': 'celegans',
        'scientific_name': 'Caenorhabditis elegans',
        'ncbi_taxon_id': '6239',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def fly_organism(testapp):
    item = {
        'ncbi_taxon_id': "7227",
        'name': "dmelanogaster",
        'scientific_name': "Drosophila melanogaster"
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


@pytest.fixture
def organism_0_0():
    return{
        'name': 'mouse',
        'ncbi_taxon_id': '9031'
    }


@pytest.fixture
def organism_1_0(organism_0_0):
    item = organism_0_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def organism_4_0(organism_0_0):
    item = organism_0_0.copy()
    item.update({
        'schema_version': '4',
        'status': 'current',
    })
    return item


@pytest.fixture
def human(testapp):
    item = {
        'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'ncbi_taxon_id': '9606',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def mouse(testapp):
    item = {
        'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'ncbi_taxon_id': '10090',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def fly(testapp):
    item = {
        'uuid': 'ab546d43-8e2a-4567-8db7-a217e6d6eea0',
        'name': 'dmelanogaster',
        'scientific_name': 'Drosophila melanogaster',
        'ncbi_taxon_id': '7227',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]
