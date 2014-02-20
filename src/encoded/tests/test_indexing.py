""" Test full indexing setup

The fixtures in this module setup a full system with postgresql and
elasticsearch running as subprocesses.
"""

import pytest

pytestmark = [pytest.mark.indexing]


@pytest.mark.fixture_lock('encoded.storage.DBSession')
@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, postgresql_server):
    from .conftest import _app_settings
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % server_host_port
    settings['elasticsearch.server'] = elasticsearch_server
    settings['sqlalchemy.url'] = postgresql_server
    settings['datastore'] = 'elasticsearch'
    return settings


@pytest.yield_fixture(scope='session')
def app(app_settings):
    from encoded.storage import DBSession

    DBSession.remove()
    DBSession.configure(bind=None)

    from encoded import main
    app = main({}, **app_settings)

    yield app

    # Dispose connections so postgres can tear down
    DBSession.bind.pool.dispose()
    DBSession.remove()
    DBSession.configure(bind=None)


@pytest.fixture(autouse=True)
def teardown(app, dbapi_conn):
    from encoded.commands import create_mapping
    create_mapping.run(app)
    cursor = dbapi_conn.cursor()
    cursor.execute("""TRUNCATE resources, transactions CASCADE;""")
    cursor.close()


@pytest.fixture
def external_tx():
    pass


@pytest.fixture
def indexer_testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'INDEXER',
    }
    return TestApp(app, environ)


@pytest.yield_fixture
def dbapi_conn(app):
    from encoded.storage import DBSession
    connection = DBSession.bind.pool.unique_connection()
    connection.detach()
    conn = connection.connection
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.yield_fixture
def listening_conn(dbapi_conn):
    cursor = dbapi_conn.cursor()
    cursor.execute("""LISTEN "encoded.transaction";""")
    yield dbapi_conn
    cursor.close()


@pytest.mark.slow
def test_indexing_workbook(testapp, indexer_testapp):
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['count'] == 1

    from ..loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir)
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['invalidated']

    res = testapp.get('/search/?type=biosample')
    assert res.json['total'] > 5


def test_indexing_simple(testapp, indexer_testapp):
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['count'] == 1
    assert 'txn_count' not in res.json

    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    uuid = res.json['@graph'][0]['uuid']
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['count'] == 1
    assert res.json['txn_count'] == 1
    assert res.json['invalidated'] == [uuid]
    res = testapp.get('/search/?type=testing_post_put_patch')
    assert res.json['total'] == 2


def test_listening(testapp, listening_conn):
    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    listening_conn.poll()
    assert len(listening_conn.notifies) == 1
    notify = listening_conn.notifies.pop()
    assert notify.channel == 'encoded.transaction'
    assert int(notify.payload) > 0
