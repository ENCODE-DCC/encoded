import pytest
import os
import fnmatch

SCHEMA_DIR = 'src/encoded/schemas/'
SCHEMA_FILES = [f for f in os.listdir(SCHEMA_DIR) if fnmatch.fnmatch(f, '*.json')]


@pytest.mark.parametrize('schema', SCHEMA_FILES)
def test_load_schema(schema):
    from encoded.schema_utils import load_schema
    assert load_schema(schema)


def test_linkTo_saves_uuid(testapp):
    from .sample_data import URL_COLLECTION
    url = '/labs/'
    lab = URL_COLLECTION[url][0]
    testapp.post_json(url, lab, status=201)
    url = '/users/'
    user = URL_COLLECTION[url][0]
    testapp.post_json(url, user, status=201)
    assert user['submits_for'] == ['cherry']

    from ..contentbase import LOCATION_ROOT
    root = testapp.app.registry[LOCATION_ROOT]
    item = root['users'][user['uuid']]
    assert item.properties['submits_for'] == [lab['uuid']]


def test_mixinProperties():
    from ..schema_utils import load_schema
    schema = load_schema('access_key.json')
    assert schema['properties']['uuid']['type'] == 'string'
