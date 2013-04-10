'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
import pytest
from pytest import fixture

app_settings = {
    'multiauth.policies': 'authtkt remoteuser',
    'multiauth.groupfinder': 'encoded.authorization.groupfinder',
    'multiauth.policy.authtkt.use': 'pyramid.authentication.AuthTktAuthenticationPolicy',
    'multiauth.policy.authtkt.hashalg': 'sha512',
    'multiauth.policy.authtkt.secret': 'GLIDING LIKE A WHALE',
    'multiauth.policy.remoteuser.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
    'multiauth.policy.remoteuser.namespace': 'remoteuser',
    'multiauth.policy.remoteuser.base': 'pyramid.authentication.RemoteUserAuthenticationPolicy',
    'persona.audiences': 'http://localhost:6543',
    'persona.siteName': 'ENCODE DCC Submission',
    'load_test_only': True,
    'load_sample_data': False,
}

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def pytest_addoption(parser):
    parser.addoption('--engine-url', dest='engine_url', default='sqlite://')


@fixture
def config(request):
    from pyramid.testing import setUp, tearDown
    request.addfinalizer(tearDown)
    return setUp()


@fixture
def dummy_request():
    from pyramid.testing import DummyRequest
    return DummyRequest()


@fixture(scope='session')
def app(request, check_constraints, zsa_savepoints):
    '''WSGI application level functional testing.
    '''
    from encoded import main
    return main({}, **app_settings)


@pytest.datafixture
def workbook(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    from ..loadxl import load_all
    from pkg_resources import resource_filename
    workbook = resource_filename('encoded', 'tests/data/test_encode3_interface_submissions.xlsx')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_test_only = app_settings.get('load_test_only', False)
    assert load_test_only
    load_all(testapp, workbook, docsdir, test=load_test_only)


@fixture
def htmltestapp(request, app, external_tx, zsa_savepoints):
    from webtest import TestApp
    return TestApp(app)


@fixture
def testapp(request, app, external_tx, zsa_savepoints):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


@fixture(scope='session')
def _server(request, app, zsa_savepoints):
    from webtest.http import StopableWSGIServer
    server = StopableWSGIServer.create(app)
    assert server.wait()

    @request.addfinalizer
    def shutdown():
        server.shutdown()

    return server


@fixture
def server(_server, external_tx):
    return _server


# http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#joining-a-session-into-an-external-transaction
# By binding the SQLAlchemy Session to an external transaction multiple testapp
# requests can be rolled back at the end of the test.

@pytest.datafixture_connection_factory
def connection_factory(config, name):
    from encoded import configure_engine
    from encoded.storage import Base, DBSession
    from sqlalchemy.orm.scoping import ScopedRegistry

    scopefunc = config.pluginmanager.getplugin('data').scopefunc

    if type(DBSession.registry) is not ScopedRegistry:
        DBSession.registry = ScopedRegistry(DBSession.session_factory, scopefunc)

    engine_settings = {
        'sqlalchemy.url': config.option.engine_url,
    }

    engine = configure_engine(engine_settings, test_setup=True)
    connection = engine.connect()
    tx = connection.begin()
    try:
        if engine.url.drivername == 'postgresql':
            # Create the different test sets in different schemas
            if name is None:
                schema_name = 'tests'
            else:
                schema_name = 'tests_%s' % name
            connection.execute('CREATE SCHEMA %s' % schema_name)
            connection.execute('SET search_path TO %s,public' % schema_name)
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
def zsa_savepoints(request, connection_proxy):
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
            self.state = 'completion'
            self.sp.commit()
            self.sp = None
            self.state = 'done'

        def newTransaction(self, transaction):
            self.state = 'new'
            self.sp = self.connection.begin_nested()
            self.state = 'begun'

    zsa_savepoints = Savepoints(connection_proxy)

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
def check_constraints(request, connection_proxy):
    '''Check deffered constraints on zope transaction commit.

    Deferred foreign key constraints are only checked at the outer transaction
    boundary, not at a savepoint. With the Pyramid transaction bound to a
    subtransaction check them manually.

    Sadly SQLite does not support manual constraint checking.
    '''
    from encoded.storage import DBSession
    from transaction.interfaces import ISynchronizer
    from zope.interface import implementer

    @implementer(ISynchronizer)
    class CheckConstraints(object):
        def __init__(self, connection):
            self.connection = connection
            self.enabled = self.connection.engine.url.drivername != 'sqlite'
            self.state = None

        def beforeCompletion(self, transaction):
            pass

        def afterCompletion(self, transaction):
            pass

        def newTransaction(self, transaction):
            if not self.enabled:
                return

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

    check_constraints = CheckConstraints(connection_proxy)

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
    from sqlalchemy import event

    class Counter(object):
        def __init__(self):
            self.reset()
            self.conn = connection

        def reset(self):
            self.count = 0

    counter = Counter()

    @event.listens_for(connection, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Ignore the testing savepoints
        if zsa_savepoints.state != 'begun' or check_constraints.state == 'checking':
            return
        counter.count += 1

    @request.addfinalizer
    def remove():
        # http://www.sqlalchemy.org/trac/ticket/2686
        # event.remove(connection, 'after_cursor_execute', after_cursor_execute)
        connection.dispatch.after_cursor_execute.remove(after_cursor_execute, connection)

    connection._has_events = True

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
