'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pkg_resources
import pytest
from pytest import fixture


pytest_plugins = [
    'encoded.tests.fixtures.shared_fixtures',
    'snovault.tests.serverfixtures',
    'snovault.tests.testappfixtures',
    'snovault.tests.toolfixtures',
    'snovault.tests.pyramidfixtures',

    'encoded.tests.fixtures.batch_download',
    'encoded.tests.fixtures.ontology',
    'encoded.tests.fixtures.testapp',

    'encoded.tests.fixtures.schemas.access_key',
    'encoded.tests.fixtures.schemas.antibody_lot',
    'encoded.tests.fixtures.schemas.award',
    'encoded.tests.fixtures.schemas.dataset',
    'encoded.tests.fixtures.schemas.document',
    'encoded.tests.fixtures.schemas.gene',
    'encoded.tests.fixtures.schemas.human_postnatal_donor',
    'encoded.tests.fixtures.schemas.lab',
    'encoded.tests.fixtures.schemas.library',
    'encoded.tests.fixtures.schemas.library_protocol',
    'encoded.tests.fixtures.schemas.matrix_file',
    'encoded.tests.fixtures.schemas.mouse_donor',
    'encoded.tests.fixtures.schemas.ontology_term',
    'encoded.tests.fixtures.schemas.organism',
    'encoded.tests.fixtures.schemas.page',
    'encoded.tests.fixtures.schemas.publication',
    'encoded.tests.fixtures.schemas.raw_sequence_file',
    'encoded.tests.fixtures.schemas.sequence_alignment_file',
    'encoded.tests.fixtures.schemas.sequencing_run',
    'encoded.tests.fixtures.schemas.suspension',
    'encoded.tests.fixtures.schemas.tissue',
    'encoded.tests.fixtures.schemas.treatment',
    'encoded.tests.fixtures.schemas.user',

]


@pytest.fixture(autouse=True)
def autouse_external_tx(external_tx):
    pass


_app_settings = {
    'collection_datastore': 'database',
    'item_datastore': 'database',
    'multiauth.policies': 'auth0 session remoteuser accesskey',
    'multiauth.groupfinder': 'encoded.authorization.groupfinder',
    'multiauth.policy.auth0.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.auth0.base': 'encoded.auth0.Auth0AuthenticationPolicy',
    'multiauth.policy.auth0.namespace': 'auth0',
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
    'load_test_only': True,
    'testing': True,
    'stage_for_followup': 'vis_indexer, region_indexer',
    'pyramid.debug_authorization': True,
    'postgresql.statement_timeout': 20,
    'retry.attempts': 3,
    'ontology_path': pkg_resources.resource_filename('encoded', '../../ontology.json'),
}


@fixture(scope='session')
def app_settings(request, wsgi_server_host_port, conn, DBSession):
    from snovault import DBSESSION
    settings = _app_settings.copy()
    settings['auth0.audiences'] = 'http://%s:%s' % wsgi_server_host_port
    settings[DBSESSION] = DBSession
    return settings


@fixture(scope='session')
def app(app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded import main
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

        from encoded.loadxl import load_all
        from pkg_resources import resource_filename
        inserts = resource_filename('encoded', 'tests/data/inserts/')
        docsdir = [resource_filename('encoded', 'tests/data/documents/')]
        load_all(testapp, inserts, docsdir)

        yield
    finally:
        tx.rollback()
