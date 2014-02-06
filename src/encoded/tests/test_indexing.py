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


@pytest.fixture(scope='session')
def app(request, app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded.storage import DBSession

    DBSession.remove()
    DBSession.configure(bind=None)

    from encoded import main
    app = main({}, **app_settings)

    from encoded.commands import create_mapping
    create_mapping.run(app)

    @request.addfinalizer
    def teardown_app():
        # Dispose connections so postgres can tear down
        DBSession.bind.pool.dispose()
        DBSession.remove()
        DBSession.configure(bind=None)

    return app


@pytest.fixture
def testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@pytest.yield_fixture
def dbapi_conn(app):
    from encoded.storage import DBSession
    connection = DBSession.bind.pool.unique_connection()
    connection.detach()
    conn = connection.connection
    yield conn
    conn.close()


@pytest.yield_fixture
def listening_conn(dbapi_conn):
    dbapi_conn.autocommit = True
    cursor = dbapi_conn.cursor()
    cursor.execute("""LISTEN "encoded.transaction";""")
    yield dbapi_conn
    cursor.close()


@pytest.mark.slow
def test_indexing_workbook(testapp):
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir)
    res = testapp.post_json('/index', {})
    assert res.json['invalidated']


def test_indexing(testapp):
    res = testapp.post_json('/index', {})
    assert res.json['txn_count'] == 0
    assert res.json['invalidated'] == []
    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    uuid = res.json['@graph'][0]['uuid']
    res = testapp.post_json('/index', {})
    assert res.json['txn_count'] == 1
    assert res.json['invalidated'] == [uuid]


def test_listening(testapp, listening_conn):
    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    listening_conn.poll()
    assert len(listening_conn.notifies) == 1
    notify = listening_conn.notifies.pop()
    assert notify.channel == 'encoded.transaction'
    assert int(notify.payload) > 0
