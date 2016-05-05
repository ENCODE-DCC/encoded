'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pkg_resources
import pytest
from pytest import fixture

pytest_plugins = [
    'encoded.tests.datafixtures',
    'snovault.tests.serverfixtures',
]


@pytest.fixture(autouse=True)
def autouse_external_tx(external_tx):
    pass


_app_settings = {
    'collection_datastore': 'database',
    'item_datastore': 'database',
    'multiauth.policies': 'persona session remoteuser accesskey',
    'multiauth.groupfinder': 'encoded.authorization.groupfinder',
    'multiauth.policy.persona.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.persona.base': 'encoded.persona.PersonaAuthenticationPolicy',
    'multiauth.policy.persona.namespace': 'persona',
    'multiauth.policy.session.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.session.base': 'pyramid.authentication.SessionAuthenticationPolicy',
    'multiauth.policy.session.namespace': 'mailto',
    'multiauth.policy.remoteuser.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.remoteuser.namespace': 'remoteuser',
    'multiauth.policy.remoteuser.base': 'pyramid.authentication.RemoteUserAuthenticationPolicy',
    'multiauth.policy.accesskey.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.accesskey.namespace': 'accesskey',
    'multiauth.policy.accesskey.base': 'encoded.authentication.BasicAuthAuthenticationPolicy',
    'multiauth.policy.accesskey.check': 'encoded.authentication.basic_auth_check',
    'persona.audiences': 'http://localhost:6543',
    'persona.verifier': 'browserid.LocalVerifier',
    'persona.siteName': 'ENCODE DCC Submission',
    'load_test_only': True,
    'testing': True,
    'pyramid.debug_authorization': True,
    'postgresql.statement_timeout': 20,
    'tm.attempts': 3,
    'ontology_path': pkg_resources.resource_filename('encoded', '../../ontology.json'),
}


@fixture(scope='session')
def app_settings(request, wsgi_server_host_port, connection, DBSession):
    from snovault import DBSESSION
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % wsgi_server_host_port
    settings[DBSESSION] = DBSession
    return settings


def pytest_configure():
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.DEBUG)

    class Shorten(logging.Filter):
        max_len = 500

        def filter(self, record):
            if record.msg == '%r':
                record.msg = record.msg % record.args
                record.args = ()
            if len(record.msg) > self.max_len:
                record.msg = record.msg[:self.max_len] + '...'
            return True

    logging.getLogger('sqlalchemy.engine.base.Engine').addFilter(Shorten())


@pytest.yield_fixture
def config():
    from pyramid.testing import setUp, tearDown
    yield setUp()
    tearDown()


@pytest.yield_fixture
def threadlocals(request, dummy_request, registry):
    from pyramid.threadlocal import manager
    manager.push({'request': dummy_request, 'registry': registry})
    yield dummy_request
    manager.pop()


from pyramid.testing import DummyRequest


class MyDummyRequest(DummyRequest):
    def remove_conditional_headers(self):
        pass

    def _get_registry(self):
        from pyramid.threadlocal import get_current_registry
        if self._registry is None:
            return get_current_registry()
        return self._registry

    def _set_registry(self, registry):
        self.__dict__['registry'] = registry

    def _del_registry(self):
        self._registry = None

    registry = property(_get_registry, _set_registry, _del_registry)


@fixture
def dummy_request(root, registry, app):
    from pyramid.request import apply_request_extensions
    request = app.request_factory.blank('/dummy')
    request.root = root
    request.registry = registry
    request._stats = {}
    request.invoke_subrequest = app.invoke_subrequest
    apply_request_extensions(request)
    return request


@fixture(scope='session')
def app(app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded import main
    return main({}, **app_settings)


@fixture
def registry(app):
    return app.registry


@fixture
def elasticsearch(registry):
    from snovault.elasticsearch import ELASTIC_SEARCH
    return registry[ELASTIC_SEARCH]


@fixture
def upgrader(registry):
    from snovault import UPGRADER
    return registry[UPGRADER]


@fixture
def root(registry):
    from snovault import ROOT
    return registry[ROOT]


@pytest.mark.fixture_cost(500)
@pytest.yield_fixture(scope='session')
def workbook(connection, app, app_settings):
    tx = connection.begin_nested()
    try:
        from webtest import TestApp
        environ = {
            'HTTP_ACCEPT': 'application/json',
            'REMOTE_USER': 'TEST',
        }
        testapp = TestApp(app, environ)

        from ..loadxl import load_all
        from pkg_resources import resource_filename
        inserts = resource_filename('encoded', 'tests/data/inserts/')
        docsdir = [resource_filename('encoded', 'tests/data/documents/')]
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
def testapp(app):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@fixture
def anontestapp(app):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
    }
    return TestApp(app, environ)


@fixture
def authenticated_testapp(app):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST_AUTHENTICATED',
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


@pytest.fixture
def indexer_testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'INDEXER',
    }
    return TestApp(app, environ)


@pytest.fixture
def embed_testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'EMBED',
    }
    return TestApp(app, environ)
