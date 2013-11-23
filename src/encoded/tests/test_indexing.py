""" Test full indexing setup

The fixtures in this module setup a full system with postgresql and
elasticsearch running as subprocesses.
"""

import pytest

pytestmark = [pytest.mark.indexing]


@pytest.yield_fixture(scope='session')
def postgresql_server():
    from urllib import quote
    from .postgresql_fixture import server_process
    tmpdir = str(pytest.ensuretemp('postgresql'))
    process = server_process(tmpdir)

    yield 'postgresql://postgres@:5432/postgres?host=%s' % quote(tmpdir)

    if process.poll() is None:
        process.terminate()
        process.wait()


@pytest.fixture(scope='session')
def elasticsearch_host_port():
    from webtest.http import get_free_port
    return get_free_port()


@pytest.yield_fixture(scope='session')
def elasticsearch_server(elasticsearch_host_port):
    from .elasticsearch_fixture import server_process
    host, port = elasticsearch_host_port
    tmpdir = pytest.ensuretemp('elasticsearch')
    process = server_process(str(tmpdir), host=host, port=port)

    yield 'http://%s:%d' % (host, port)

    if process.poll() is None:
        process.terminate()
        process.wait()


@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, postgresql_server):
    from .conftest import _app_settings
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % server_host_port
    settings['elasticsearch.server'] = elasticsearch_server
    settings['sqlalchemy.url'] = postgresql_server
    settings['collection_source'] = 'elasticsearch'
    return settings


# Renamed because https://bitbucket.org/hpk42/pytest/issue/392

@pytest.yield_fixture(scope='session')
def real_app(app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded import main
    app = main({}, **app_settings)

    from encoded.commands import create_mapping
    create_mapping.run(app)

    yield app

    # Dispose connections so postgres can tear down
    from encoded.storage import DBSession
    DBSession.bind.pool.dispose()
    DBSession.remove()
    DBSession.configure(bind=None)


@pytest.fixture
def real_testapp(real_app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(real_app, environ)


@pytest.yield_fixture
def dbapi_conn(real_app):
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


def test_indexing_workbook(real_testapp):
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(real_testapp, inserts, docsdir)
    res = real_testapp.post_json('/index', {})
    assert res.json['invalidated']


def test_indexing(real_testapp):
    res = real_testapp.post_json('/index', {})
    assert res.json['txn_count'] == 0
    assert res.json['invalidated'] == []
    res = real_testapp.post_json('/testing-post-put-patch/', {'required': ''})
    uuid = res.json['@graph'][0]['uuid']
    res = real_testapp.post_json('/index', {})
    assert res.json['txn_count'] == 1
    assert res.json['invalidated'] == [uuid]


def test_listening(real_testapp, listening_conn):
    res = real_testapp.post_json('/testing-post-put-patch/', {'required': ''})
    listening_conn.poll()
    assert len(listening_conn.notifies) == 1
    notify = listening_conn.notifies.pop()
    assert notify.channel == 'encoded.transaction'
    assert int(notify.payload) > 0
