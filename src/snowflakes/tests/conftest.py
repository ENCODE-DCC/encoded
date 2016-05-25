'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pkg_resources
import pytest
from pytest import fixture

pytest_plugins = [
    'snowflakes.tests.datafixtures',
    'snovault.tests.serverfixtures',
    'snovault.tests.testappfixtures',
    'snovault.tests.toolfixtures',
    'snovault.tests.pyramidfixtures',
]


@pytest.fixture(autouse=True)
def autouse_external_tx(external_tx):
    pass


_app_settings = {
    'collection_datastore': 'database',
    'item_datastore': 'database',
    'multiauth.policies': 'persona session remoteuser accesskey',
    'multiauth.groupfinder': 'snowflakes.authorization.groupfinder',
    'multiauth.policy.persona.use': 'snovault.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.persona.base': 'snowflakes.persona.PersonaAuthenticationPolicy',
    'multiauth.policy.persona.namespace': 'persona',
    'multiauth.policy.session.use': 'snovault.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.session.base': 'pyramid.authentication.SessionAuthenticationPolicy',
    'multiauth.policy.session.namespace': 'mailto',
    'multiauth.policy.remoteuser.use': 'snovault.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.remoteuser.namespace': 'remoteuser',
    'multiauth.policy.remoteuser.base': 'pyramid.authentication.RemoteUserAuthenticationPolicy',
    'multiauth.policy.accesskey.use': 'snovault.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.accesskey.namespace': 'accesskey',
    'multiauth.policy.accesskey.base': 'snovault.authentication.BasicAuthAuthenticationPolicy',
    'multiauth.policy.accesskey.check': 'snovault.authentication.basic_auth_check',
    'persona.audiences': 'http://localhost:6543',
    'persona.verifier': 'browserid.LocalVerifier',
    'persona.siteName': 'ENCODE DCC Submission',
    'load_test_only': True,
    'testing': True,
    'pyramid.debug_authorization': True,
    'postgresql.statement_timeout': 20,
    'tm.attempts': 3,
    'ontology_path': pkg_resources.resource_filename('snowflakes', '../../ontology.json'),
}


@fixture(scope='session')
def app_settings(request, wsgi_server_host_port, conn, DBSession):
    from snovault import DBSESSION
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % wsgi_server_host_port
    settings[DBSESSION] = DBSession
    return settings


@fixture(scope='session')
def app(app_settings):
    '''WSGI application level functional testing.
    '''
    from snowflakes import main
    return main({}, **app_settings)


@pytest.mark.fixture_cost(500)
@pytest.yield_fixture(scope='session')
def workbook(conn, app, app_settings):
    tx = conn.begin_nested()
    try:
        from webtest import TestApp
        environ = {
            'HTTP_ACCEPT': 'application/json',
            'REMOTE_USER': 'TEST',
        }
        testapp = TestApp(app, environ)

        from ..loadxl import load_all
        from pkg_resources import resource_filename
        inserts = resource_filename('snowflakes', 'tests/data/inserts/')
        docsdir = [resource_filename('snowflakes', 'tests/data/documents/')]
        load_all(testapp, inserts, docsdir)

        yield
    finally:
        tx.rollback()


@fixture
def anonhtmltestapp(app):
    from webtest import TestApp
    return TestApp(app)


@fixture
def htmltestapp(app):
    from webtest import TestApp
    environ = {
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@fixture
def submitter_testapp(app):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST_SUBMITTER',
    }
    return TestApp(app, environ)
