'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pytest
from pytest import fixture

_app_settings = {
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
    'allow.list': 'Everyone',
    'allow.traverse': 'Everyone',
    'allow.search': 'Everyone',
    'allow.ALL_PERMISSIONS': 'group.admin',
    'allow.edw_key_create': 'accesskey.edw',
    'allow.edw_key_update': 'accesskey.edw',
    'load_test_only': True,
    'load_sample_data': False,
    'testing': True,
    'pyramid.debug_authorization': True,
    'postgresql.statement_timeout': 20,
}


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def engine_url(request):
    engine_url = request.session.config.option.engine_url
    if engine_url is not None:
        yield engine_url
        return

    # Ideally this would use a different database on the same postgres server
    from urllib import quote
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


@fixture
def dummy_request(root, registry):
    from pyramid.testing import DummyRequest
    return DummyRequest(root=root, registry=registry, _stats={})


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
    from ..indexing import ELASTIC_SEARCH
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


@fixture(scope='session')
def server_host_port():
    from webtest.http import get_free_port
    return get_free_port()


@fixture(scope='session')
def authenticated_app(app):
    import Cookie
    def wsgi_filter(environ, start_response):
        # set REMOTE_USER from cookie
        cookies = Cookie.SimpleCookie()
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

@pytest.mark.fixture_lock('encoded.storage.DBSession')
@pytest.yield_fixture(scope='session')
def connection(request, engine_url):
    from encoded import configure_engine
    from encoded.storage import Base, DBSession
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
    print 'BEGIN external_tx'
    tx = connection.begin_nested()
    request.addfinalizer(tx.rollback)
    ## The database should be empty unless a data fixture was loaded
    # from encoded.storage import Base
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
    from encoded.storage import DBSession
    return DBSession()


@fixture(scope='session')
def check_constraints(request, connection):
    '''Check deffered constraints on zope transaction commit.

    Deferred foreign key constraints are only checked at the outer transaction
    boundary, not at a savepoint. With the Pyramid transaction bound to a
    subtransaction check them manually.
    '''
    from encoded.storage import DBSession
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
    from encoded.storage import DBSession
    from sqlalchemy import event

    session = DBSession()

    @event.listens_for(session, 'after_flush')
    def check_dependencies(session, flush_context):
        #import pytest; pytest.set_trace()
        assert not flush_context.cycles

    @event.listens_for(connection, "before_execute", retval=True)
    def before_execute(conn, clauseelement, multiparams, params):
        #import pytest; pytest.set_trace()
        return clauseelement, multiparams, params

    @request.addfinalizer
    def remove():
        event.remove(session, 'before_flush', check_dependencies)


@pytest.fixture
def labs(testapp):
    from . import sample_data
    return sample_data.load(testapp, 'lab')


@pytest.fixture
def lab(labs):
    return [l for l in labs if l['name'] == 'myers'][0]


@pytest.fixture
def users(testapp, labs):
    from . import sample_data
    return sample_data.load(testapp, 'user')


@pytest.fixture
def wrangler(users):
    return [u for u in users if 'wrangler' in u.get('groups', ())][0]


@pytest.fixture
def submitter(users, lab):
    return [u for u in users if lab['@id'] in u['submits_for']][0]


@pytest.fixture
def awards(testapp):
    from . import sample_data
    return sample_data.load(testapp, 'award')


@pytest.fixture
def award(awards):
    return [a for a in awards if a['name'] == 'Myers'][0]


@pytest.fixture
def sources(testapp):
    from . import sample_data
    return sample_data.load(testapp, 'source')


@pytest.fixture
def source(sources):
    return [s for s in sources if s['name'] == 'sigma'][0]


@pytest.fixture
def organisms(testapp):
    from . import sample_data
    return sample_data.load(testapp, 'organism')


@pytest.fixture
def organism(organisms):
    return [o for o in organisms if o['name'] == 'human'][0]


@pytest.fixture
def biosamples(testapp, labs, awards, sources, organisms):
    from . import sample_data
    return sample_data.load(testapp, 'biosample')


@pytest.fixture
def biosample(biosamples):
    return [b for b in biosamples if b['accession'] == 'ENCBS000TST'][0]


@pytest.fixture
def libraries(testapp, labs, awards, biosamples):
    from . import sample_data
    return sample_data.load(testapp, 'library')


@pytest.fixture
def library(libraries):
    return [l for l in libraries if l['accession'] == 'ENCLB000TST'][0]


@pytest.fixture
def experiments(testapp, labs, awards):
    from . import sample_data
    return sample_data.load(testapp, 'experiment')


@pytest.fixture
def experiment(experiments):
    return [e for e in experiments if e['accession'] == 'ENCSR000TST'][0]


@pytest.fixture
def replicates(testapp, experiments, libraries):
    from . import sample_data
    return sample_data.load(testapp, 'replicate')


@pytest.fixture
def replicate(replicates):
    return replicates[0]


@pytest.fixture
def files(testapp, experiments):
    from . import sample_data
    return sample_data.load(testapp, 'file')


@pytest.fixture
def file(files):
    return [f for f in files if f['accession'] == 'ENCFF000TST'][0]


@pytest.fixture
def antibody_lots(testapp, labs, awards, sources, organisms, targets):
    from . import sample_data
    return sample_data.load(testapp, 'antibody_lot')


@pytest.fixture
def antibody_lot(antibody_lots):
    return [al for al in antibody_lots if al['accession'] == 'ENCAB000TST'][0]


@pytest.fixture
def targets(testapp,organisms):
    from . import sample_data
    return sample_data.load(testapp, 'target')


@pytest.fixture
def target(targets):
    return [t for t in targets if t['label'] == 'ATF4'][0]


@pytest.fixture
def rnais(testapp,labs, awards, targets):
    from . import sample_data
    return sample_data.load(testapp, 'rnai')


@pytest.fixture
def rnai(rnais):
    return [r for r in rnais if r['rnai_type'] == 'shRNA'][0]


@pytest.fixture
def constructs(testapp,labs, awards, targets, sources):
    from . import sample_data
    return sample_data.load(testapp, 'construct')


@pytest.fixture
def construct(constructs):
    return [c for c in constructs if c['construct_type'] == 'fusion protein'][0]


@pytest.fixture
def datasets(testapp, labs, awards):
    from . import sample_data
    return sample_data.load(testapp, 'dataset')


@pytest.fixture
def dataset(datasets):
    return [d for d in datasets if d['accession'] == 'ENCSR002TST'][0]

@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def postgresql_server(request):
    from urllib import quote
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
