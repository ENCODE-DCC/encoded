import pytest
from pkg_resources import resource_listdir

SCHEMA_FILES = [
    f for f in resource_listdir('encoded', 'schemas')
    if f.endswith('.json')
]


@pytest.mark.parametrize('schema', SCHEMA_FILES)
def test_load_schema(schema):
    from encoded.schema_utils import load_schema
    assert load_schema(schema)


def test_linkTo_saves_uuid(testapp, users):
    from .sample_data import URL_COLLECTION
    lab = URL_COLLECTION['lab'][0]
    user = URL_COLLECTION['user'][0]
    assert user['submits_for'] == ['cherry']

    from ..contentbase import LOCATION_ROOT
    root = testapp.app.registry[LOCATION_ROOT]
    item = root['users'][user['uuid']]
    assert item.properties['submits_for'] == [lab['uuid']]


def test_mixinProperties():
    from ..schema_utils import load_schema
    schema = load_schema('access_key.json')
    assert schema['properties']['uuid']['type'] == 'string'


def test_dependencies(testapp):
    collection_url = '/testing-dependencies/'
    testapp.post_json(collection_url, {'dep1': 'dep1', 'dep2': 'dep2'}, status=201)
    testapp.post_json(collection_url, {'dep1': 'dep1'}, status=422)
    testapp.post_json(collection_url, {'dep2': 'dep2'}, status=422)
    testapp.post_json(collection_url, {'dep1': 'dep1', 'dep2': 'disallowed'}, status=422)


def test_page_schema_validates_parent_is_not_collection_default_page(testapp):
    res = testapp.post_json('/pages/', {'name': 'biosamples', 'title': 'Biosamples'})
    uuid = res.json['@graph'][0]['@id']
    testapp.post_json('/pages/', {'parent': uuid, 'name': 'test', 'title': 'Test'}, status=422)
