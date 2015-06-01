'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pkg_resources
import pytest
from pytest import fixture

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
    'ontology_path': pkg_resources.resource_filename('encoded', '../../ontology.json'),
}


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def engine_url(request):
    engine_url = request.session.config.option.engine_url
    if engine_url is not None:
        yield engine_url
        return

    # Ideally this would use a different database on the same postgres server
    from urllib.parse import quote
    from .postgresql_fixture import initdb, server_process
    tmpdir = request.config._tmpdirhandler.mktemp('postgresql-engine', numbered=True)
    tmpdir = str(tmpdir)
    initdb(tmpdir)
    process = server_process(tmpdir)

    yield 'postgresql://postgres@:5432/postgres?host=%s' % quote(tmpdir)

    if process.poll() is None:
        process.terminate()
        process.wait()


@fixture(scope='session')
def app_settings(request, server_host_port, connection):
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % server_host_port
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


@fixture
def config(request):
    from pyramid.testing import setUp, tearDown
    request.addfinalizer(tearDown)
    return setUp()


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
def app(zsa_savepoints, check_constraints, app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded import main
    return main({}, **app_settings)


@fixture
def registry(app):
    return app.registry


@fixture
def elasticsearch(registry):
    from contentbase.elasticsearch import ELASTIC_SEARCH
    return registry[ELASTIC_SEARCH]


@fixture
def root(app):
    return app.root_factory(app)


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
def anonhtmltestapp(app, external_tx):
    from webtest import TestApp
    return TestApp(app)


@fixture
def htmltestapp(app, external_tx):
    from webtest import TestApp
    environ = {
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@fixture
def testapp(app, external_tx):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@fixture
def anontestapp(app, external_tx):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
    }
    return TestApp(app, environ)


@fixture
def authenticated_testapp(app, external_tx):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST_AUTHENTICATED',
    }
    return TestApp(app, environ)


@fixture
def submitter_testapp(app, external_tx):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST_SUBMITTER',
    }
    return TestApp(app, environ)


@pytest.fixture
def indexer_testapp(app, external_tx):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'INDEXER',
    }
    return TestApp(app, environ)


@pytest.fixture
def embed_testapp(app, external_tx):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'EMBED',
    }
    return TestApp(app, environ)


@fixture(scope='session')
def server_host_port():
    from webtest.http import get_free_port
    return get_free_port()


@fixture(scope='session')
def authenticated_app(app):
    from http.cookies import SimpleCookie

    def wsgi_filter(environ, start_response):
        # set REMOTE_USER from cookie
        cookies = SimpleCookie()
        cookies.load(environ.get('HTTP_COOKIE', ''))
        if 'REMOTE_USER' in cookies:
            user = cookies['REMOTE_USER'].value
        else:
            user = 'TEST_AUTHENTICATED'
        environ['REMOTE_USER'] = user
        return app(environ, start_response)
    return wsgi_filter


@pytest.mark.fixture_cost(100)
@fixture(scope='session')
def _server(request, authenticated_app, server_host_port):
    from webtest.http import StopableWSGIServer
    host, port = server_host_port

    server = StopableWSGIServer.create(
        authenticated_app,
        host=host,
        port=port,
        threads=1,
        channel_timeout=60,
        cleanup_interval=10,
        expose_tracebacks=True,
    )
    assert server.wait()

    @request.addfinalizer
    def shutdown():
        server.shutdown()

    return 'http://%s:%s' % server_host_port


@fixture
def server(_server, external_tx):
    return _server


# http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#joining-a-session-into-an-external-transaction
# By binding the SQLAlchemy Session to an external transaction multiple testapp
# requests can be rolled back at the end of the test.

@pytest.mark.fixture_lock('contentbase.storage.DBSession')
@pytest.yield_fixture(scope='session')
def connection(request, engine_url):
    from encoded import configure_engine
    from contentbase.storage import Base, DBSession
    from sqlalchemy.orm.scoping import ScopedRegistry

    # ``server`` thread must be in same scope
    if type(DBSession.registry) is not ScopedRegistry:
        DBSession.registry = ScopedRegistry(DBSession.session_factory, lambda: 0)

    engine_settings = {
        'sqlalchemy.url': engine_url,
    }

    engine = configure_engine(engine_settings, test_setup=True)
    connection = engine.connect()
    tx = connection.begin()
    try:
        Base.metadata.create_all(bind=connection)
        session = DBSession(scope=None, bind=connection)
        DBSession.registry.set(session)
        yield connection
    finally:
        tx.rollback()
        connection.close()
        engine.dispose()


@fixture
def external_tx(request, connection):
    print('BEGIN external_tx')
    tx = connection.begin_nested()
    request.addfinalizer(tx.rollback)
    # # The database should be empty unless a data fixture was loaded
    # from contentbase.storage import Base
    # for table in Base.metadata.sorted_tables:
    #     assert connection.execute(table.count()).scalar() == 0
    return tx


@fixture
def transaction(request, external_tx, zsa_savepoints, check_constraints):
    import transaction
    transaction.begin()
    request.addfinalizer(transaction.abort)
    return transaction


@fixture(scope='session')
def zsa_savepoints(request, connection):
    """ Place a savepoint at the start of the zope transaction

    This means failed requests rollback to the db state when they began rather
    than that at the start of the test.
    """
    from transaction.interfaces import ISynchronizer
    from zope.interface import implementer

    @implementer(ISynchronizer)
    class Savepoints(object):
        def __init__(self, connection):
            self.connection = connection
            self.sp = None
            self.state = None

        def beforeCompletion(self, transaction):
            pass

        def afterCompletion(self, transaction):
            # txn be aborted a second time in manager.begin()
            if self.sp is None:
                return
            if self.state == 'commit':
                self.state = 'completion'
                self.sp.commit()
            else:
                self.state = 'abort'
                self.sp.rollback()
            self.sp = None
            self.state = 'done'

        def newTransaction(self, transaction):
            self.state = 'new'
            self.sp = self.connection.begin_nested()
            self.state = 'begun'
            transaction.addBeforeCommitHook(self._registerCommit)

        def _registerCommit(self):
            self.state = 'commit'

    zsa_savepoints = Savepoints(connection)

    import transaction
    transaction.manager.registerSynch(zsa_savepoints)

    @request.addfinalizer
    def unregister():
        transaction.manager.unregisterSynch(zsa_savepoints)

    return zsa_savepoints


@fixture
def session(transaction):
    """ Returns a setup session

    Depends on transaction as storage relies on some interaction there.
    """
    from contentbase.storage import DBSession
    return DBSession()


@fixture(scope='session')
def check_constraints(request, connection):
    '''Check deffered constraints on zope transaction commit.

    Deferred foreign key constraints are only checked at the outer transaction
    boundary, not at a savepoint. With the Pyramid transaction bound to a
    subtransaction check them manually.
    '''
    from contentbase.storage import DBSession
    from transaction.interfaces import ISynchronizer
    from zope.interface import implementer

    @implementer(ISynchronizer)
    class CheckConstraints(object):
        def __init__(self, connection):
            self.connection = connection
            self.state = None

        def beforeCompletion(self, transaction):
            pass

        def afterCompletion(self, transaction):
            pass

        def newTransaction(self, transaction):

            @transaction.addBeforeCommitHook
            def set_constraints():
                self.state = 'checking'
                session = DBSession()
                session.flush()
                sp = self.connection.begin_nested()
                try:
                    self.connection.execute('SET CONSTRAINTS ALL IMMEDIATE')
                except:
                    sp.rollback()
                    raise
                else:
                    self.connection.execute('SET CONSTRAINTS ALL DEFERRED')
                finally:
                    sp.commit()
                    self.state = None

    check_constraints = CheckConstraints(connection)

    import transaction
    transaction.manager.registerSynch(check_constraints)

    @request.addfinalizer
    def unregister():
        transaction.manager.unregisterSynch(check_constraints)

    return check_constraints


@fixture
def execute_counter(request, connection, zsa_savepoints, check_constraints):
    """ Count calls to execute
    """
    from contextlib import contextmanager
    from sqlalchemy import event

    class Counter(object):
        def __init__(self):
            self.reset()
            self.conn = connection

        def reset(self):
            self.count = 0

        @contextmanager
        def expect(self, count):
            start = self.count
            yield
            difference = self.count - start
            assert difference == count

    counter = Counter()

    @event.listens_for(connection, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Ignore the testing savepoints
        if zsa_savepoints.state != 'begun' or check_constraints.state == 'checking':
            return
        counter.count += 1

    @request.addfinalizer
    def remove():
        event.remove(connection, 'after_cursor_execute', after_cursor_execute)

    return counter


@fixture
def no_deps(request, connection):
    from contentbase.storage import DBSession
    from sqlalchemy import event

    session = DBSession()

    @event.listens_for(session, 'after_flush')
    def check_dependencies(session, flush_context):
        assert not flush_context.cycles

    @event.listens_for(connection, "before_execute", retval=True)
    def before_execute(conn, clauseelement, multiparams, params):
        return clauseelement, multiparams, params

    @request.addfinalizer
    def remove():
        event.remove(session, 'before_flush', check_dependencies)


@pytest.fixture
def lab(testapp):
    item = {
        'name': 'encode-lab',
        'title': 'ENCODE lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]


@fixture
def admin(testapp):
    item = {
        'first_name': 'Test',
        'last_name': 'Admin',
        'email': 'admin@example.org',
        'groups': ['admin'],
    }
    return testapp.post_json('/user', item).json['@graph'][0]


@pytest.fixture
def wrangler(testapp):
    item = {
        # antibody_characterization reviewed_by has linkEnum
        'uuid': '4c23ec32-c7c8-4ac0-affb-04befcc881d4',
        'first_name': 'Wrangler',
        'last_name': 'Admin',
        'email': 'wrangler@example.org',
        'groups': ['admin'],
    }
    return testapp.post_json('/user', item).json['@graph'][0]


@pytest.fixture
def submitter(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'encode_submitter@example.org',
        'submits_for': [lab['@id']],
    }
    return testapp.post_json('/user', item).json['@graph'][0]


@pytest.fixture
def award(testapp):
    item = {
        'name': 'encode3-award',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def encode2_award(testapp):
    item = {
        # upgrade/shared.py ENCODE2_AWARDS
        'uuid': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'name': 'encode2-award',
        'rfa': 'ENCODE2',
        'project': 'ENCODE',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def source(testapp):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich',
        'url': 'http://www.sigmaaldrich.com',
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def human(testapp):
    item = {
        'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def mouse(testapp):
    item = {
        'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def organism(human):
    return human


@pytest.fixture
def biosample(testapp, source, lab, award, organism):
    item = {
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]


@pytest.fixture
def library(testapp, lab, award, biosample):
    item = {
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample': biosample['@id'],
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def experiment(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def replicate(testapp, experiment, library):
    item = {
        'experiment': experiment['@id'],
        'library': library['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def file(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'fasta',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_dataset(testapp, lab, award, dataset):
    item = {
        'dataset': dataset['@id'],
        'file_format': 'fasta',
        'md5sum': '3f9ae164abb55a93bcd891b192d86164',
        'output_type': 'raw data',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def antibody_lot(testapp, lab, award, source, mouse, target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'targets': [target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def target(testapp, organism):
    item = {
        'label': 'ATF4',
        'organism': organism['@id'],
        'investigated_as': ['transcription factor'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


@pytest.fixture
def attachment():
    return {'download': 'red-dot.png', 'href': RED_DOT}


@pytest.fixture
def antibody_characterization(testapp, award, lab, target, antibody_lot, attachment):
    item = {
        'characterizes': antibody_lot['@id'],
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'secondary_characterization_method': 'dot blot assay',
    }
    return testapp.post_json('/antibody_characterization', item).json['@graph'][0]


@pytest.fixture
def antibody_approval(testapp, award, lab, target, antibody_lot, antibody_characterization):
    item = {
        'antibody': antibody_lot['@id'],
        'characterizations': [antibody_characterization['@id']],
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'status': 'pending dcc review',
    }
    return testapp.post_json('/antibody_approval', item).json['@graph'][0]


@pytest.fixture
def rnai(testapp, lab, award, target):
    item = {
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'rnai_sequence': 'TATATGGGGAA',
        'rnai_type': 'shRNA',
    }
    return testapp.post_json('/rnai', item).json['@graph'][0]


@pytest.fixture
def construct(testapp, lab, award, target, source):
    item = {
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'construct_type': 'fusion protein',
        'tags': [],
    }
    return testapp.post_json('/construct', item).json['@graph'][0]


@pytest.fixture
def dataset(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'dataset_type': 'composite',
    }
    return testapp.post_json('/dataset', item).json['@graph'][0]


@pytest.fixture
def publication(testapp, lab, award):
    item = {
        # upgrade/shared.py has a REFERENCES_UUID mapping.
        'uuid': '8312fc0c-b241-4cb2-9b01-1438910550ad',
        'title': "Test publication",
        'award': award['@id'],
        'lab': lab['@id'],
        'identifiers': ["doi:10.1214/11-AOAS466"],
    }
    print('submit publication')
    return testapp.post_json('/publication', item).json['@graph'][0]


@pytest.fixture
def pipeline(testapp):
    item = {
        'title': "Test pipeline",
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def document(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'document_type': 'growth protocol',
    }
    return testapp.post_json('/document', item).json['@graph'][0]


@pytest.fixture
def biosample_characterization(testapp, award, lab, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


@pytest.fixture
def mouse_donor(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def postgresql_server(request):
    from urllib.parse import quote
    from .postgresql_fixture import initdb, server_process
    tmpdir = request.config._tmpdirhandler.mktemp('postgresql', numbered=True)
    tmpdir = str(tmpdir)
    initdb(tmpdir)
    process = server_process(tmpdir)

    yield 'postgresql://postgres@:5432/postgres?host=%s' % quote(tmpdir)

    if process.poll() is None:
        process.terminate()
        process.wait()


@pytest.fixture(scope='session')
def elasticsearch_host_port():
    from webtest.http import get_free_port
    return get_free_port()


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def elasticsearch_server(request, elasticsearch_host_port):
    from .elasticsearch_fixture import server_process
    host, port = elasticsearch_host_port
    tmpdir = request.config._tmpdirhandler.mktemp('elasticsearch', numbered=True)
    tmpdir = str(tmpdir)
    process = server_process(str(tmpdir), host=host, port=port)

    yield 'http://%s:%d' % (host, port)

    if process.poll() is None:
        process.terminate()
        process.wait()
