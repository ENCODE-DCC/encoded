import pytest

pytestmark = [pytest.mark.indexing]
# Use workbook fixture from BDD tests (including elasticsearch)
from .features.conftest import app_settings, app, workbook


pytest.plugins = [
    'snovault.tests.indexfixtures',
]


@pytest.mark.slow
def test_indexing_workbook(testapp, indexer_testapp):
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['indexed'] == 1

    from encoded.loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir)
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['updated']
    assert res.json['indexed']

    res = testapp.get('/search/?type=Biosample')
    assert res.json['total'] > 5
