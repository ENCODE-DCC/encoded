'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pkg_resources
import pytest
from pytest import fixture

pytest_plugins = [
    'encoded.tests.datafixtures',
    'snovault.tests.serverfixtures',
    'snovault.tests.testappfixtures',
    'snovault.tests.toolfixtures',
    'snovault.tests.pyramidfixtures',

    'encoded.tests.fixtures.access_key',
    'encoded.tests.fixtures.analysis_step',
    'encoded.tests.fixtures.annotation',
    'encoded.tests.fixtures.antibody_characterization',
    'encoded.tests.fixtures.antibody',
    'encoded.tests.fixtures.award',
    'encoded.tests.fixtures.biosample_type',
    'encoded.tests.fixtures.biosample',
    'encoded.tests.fixtures.bismark_quality_metric'
    'encoded.tests.fixtures.cart',
    'encoded.tests.fixtures.characterization',
    'encoded.tests.fixtures.chip_peak_enrichment_quality_metric',
    'encoded.tests.fixtures.chip_peak_enrichment_quality_metric',
    'encoded.tests.fixtures.document',
    'encoded.tests.fixtures.dataset',
    'encoded.tests.fixtures.donor',
    'encoded.tests.fixtures.experiment',
    'encoded.tests.fixtures.file',
    'encoded.tests.fixtures.gene',
    'encoded.tests.fixtures.genetic_modifcation',
    'encoded.tests.fixtures.lab',
    'encoded.tests.fixtures.library',
    'encoded.tests.fixtures.long_read_rna_mapping_quality_metric',
    'encoded.tests.fixtures.organism',
    'encoded.tests.fixtures.micro_rna_mapping_quality_metric',
    'encoded.tests.fixtures.platform'
    'encoded.tests.fixtures.pipeline',
    'encoded.tests.fixtures.publication_data',
    'encoded.tests.fixtures.publication',
    'encoded.tests.fixtures.reference_epigenome',
    'encoded.tests.fixtures.replicate',
    'encoded.tests.fixtures.samtools_flagstats_quality_metric',
    'encoded.tests.fixtures.series',
    'encoded.tests.fixtures.software',
    'encoded.tests.fixtures.source',
    'encoded.tests.fixtures.target',
    'encoded.tests.fixtures.treatment',
    'encoded.tests.fixtures.ucsc_browser_composite',
    'encoded.tests.fixtures.upgrade',
    'encoded.tests.fixtures.user',



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
