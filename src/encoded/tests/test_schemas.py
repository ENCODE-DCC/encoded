import pytest
import os
import fnmatch

SCHEMA_DIR = 'src/encoded/schemas/'
SCHEMA_FILES = [f for f in os.listdir(SCHEMA_DIR) if fnmatch.fnmatch(f, '*.json')]


@pytest.mark.parametrize('schema', SCHEMA_FILES)
def test_load_schema(schema):
    from encoded.schema_utils import load_schema
    assert load_schema(schema)
