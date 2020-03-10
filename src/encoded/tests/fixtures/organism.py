import pytest
from ..constants import *


@pytest.fixture
def fly_organism(testapp):
    item = {
        'taxon_id': "7227",
        'name': "dmelanogaster",
        'scientific_name': "Drosophila melanogaster"
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]

@pytest.fixture
def base_chipmunk(testapp):
    item = {
        'name': 'chimpmunk',
        'taxon_id': '12345',
        'scientific_name': 'Chip chipmunicus'
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


@pytest.fixture
def worm(testapp):
    item = {
        'uuid': '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20',
        'name': 'celegans',
        'scientific_name': 'Caenorhabditis elegans',
        'taxon_id': '6239',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def human(testapp):
    item = {
        'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def mouse(testapp):
    item = {
        'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def fly(testapp):
    item = {
        'uuid': 'ab546d43-8e2a-4567-8db7-a217e6d6eea0',
        'name': 'dmelanogaster',
        'scientific_name': 'Drosophila melanogaster',
        'taxon_id': '7227',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


# TODO: replace yield_fixture
@pytest.yield_fixture(scope='session')
def minitestdata(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()


# TODO: replace yield_fixture
@pytest.yield_fixture(scope='session')
def minitestdata2(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()


@pytest.fixture
def organism(human):
    return human


@pytest.fixture
def organism_3():
    return{
        'name': 'mouse',
        'taxon_id': '9031'
    }


@pytest.fixture
def organism_1(organism_3):
    item = organism_3.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def organism_4(organism_3):
    item = organism_3.copy()
    item.update({
        'schema_version': '4',
        'status': 'current',
    })
    return item

