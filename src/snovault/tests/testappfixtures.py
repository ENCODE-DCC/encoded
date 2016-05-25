import pytest

_app_settings = {
    'collection_datastore': 'database',
    'item_datastore': 'database',
    'persona.audiences': 'http://localhost:6543',
    'persona.verifier': 'browserid.LocalVerifier',
    'persona.siteName': 'Snowflakes',
    'load_test_only': True,
    'testing': True,
    'pyramid.debug_authorization': True,
    'postgresql.statement_timeout': 20,
    'tm.attempts': 3,
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
}


@pytest.fixture(scope='session')
def app_settings(request, wsgi_server_host_port, conn, DBSession):
    from snovault import DBSESSION
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % wsgi_server_host_port
    settings[DBSESSION] = DBSession
    return settings


@pytest.fixture(scope='session')
def app(app_settings):
    '''WSGI application level functional testing.
       will have to make snovault dummy main app
    '''
    from snovault import main
    return main({}, **app_settings)


@pytest.fixture
def testapp(app):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@pytest.fixture
def anontestapp(app):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
    }
    return TestApp(app, environ)


@pytest.fixture
def authenticated_testapp(app):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST_AUTHENTICATED',
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


@pytest.fixture
def indexer_testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'INDEXER',
    }
    return TestApp(app, environ)
