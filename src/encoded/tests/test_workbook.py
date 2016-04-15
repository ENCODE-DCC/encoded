import pytest

pytestmark = [pytest.mark.indexing]


@pytest.fixture(scope='session')
def app_settings(wsgi_server_host_port, elasticsearch_server, postgresql_server):
    from snovault.tests import test_indexing
    return test_indexing.app_settings(wsgi_server_host_port, elasticsearch_server, postgresql_server)


@pytest.mark.slow
def test_indexing_workbook(testapp, indexer_testapp):
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['indexed'] == 1

    from ..loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir)
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['updated']
    assert res.json['indexed']

    res = testapp.get('/search/?type=Biosample')
    assert res.json['total'] > 5
