from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool
from sqlalchemy import engine_from_config
from .storage import (
    Base,
    DBSession,
)
STATIC_MAX_AGE = 0


def static_resources(config):
    from pkg_resources import resource_filename
    import mimetypes
    mimetypes.init()
    mimetypes.init([resource_filename('encoded', 'static/mime.types')])
    config.add_static_view('static', 'static', cache_max_age=STATIC_MAX_AGE)
    config.add_static_view('profiles', 'schemas', cache_max_age=STATIC_MAX_AGE)

    favicon_path = '/static/img/favicon.ico'
    if config.route_prefix:
        favicon_path = '/%s%s' % (config.route_prefix, favicon_path)
    config.add_route('favicon.ico', 'favicon.ico')

    def favicon(request):
        subreq = request.copy()
        subreq.path_info = favicon_path
        response = request.invoke_subrequest(subreq)
        return response

    config.add_view(favicon, route_name='favicon.ico')


def tests_js(config):
    config.add_static_view('tests/js', 'tests/js', cache_max_age=STATIC_MAX_AGE)


def configure_engine(settings, test_setup=False):
    engine_url = settings.get('sqlalchemy.url')
    if not engine_url:
        # Already setup by test fixture
        return None
    engine_opts = {}
    # http://docs.sqlalchemy.org/en/rel_0_8/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
    if engine_url == 'sqlite://':
        from sqlalchemy.pool import StaticPool
        engine_opts.update(
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
        )
    engine = engine_from_config(settings, 'sqlalchemy.', **engine_opts)
    if engine.url.drivername == 'sqlite':
        enable_sqlite_savepoints(engine)
    elif engine.url.drivername == 'postgresql':
        set_postgresql_statement_timeout(engine)
    if not test_setup:
        Base.metadata.create_all(engine)
        DBSession.configure(bind=engine)
    return engine


def enable_sqlite_savepoints(engine):
    """ Savepoint support for sqlite.

    https://code.google.com/p/pysqlite-static-env/
    """
    from sqlalchemy import event

    @event.listens_for(engine, 'connect')
    def connect(dbapi_connection, connection_record):
        dbapi_connection.operation_needs_transaction_callback = lambda x: True

    from zope.sqlalchemy.datamanager import NO_SAVEPOINT_SUPPORT
    NO_SAVEPOINT_SUPPORT.discard('sqlite')


def set_postgresql_statement_timeout(engine, timeout=10 * 1000):
    """ Prevent Postgres waiting indefinitely for a lock.
    """
    from sqlalchemy import event
    import psycopg2

    @event.listens_for(engine, 'connect')
    def connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SET statement_timeout TO %d" % timeout)
        except psycopg2.Error:
            dbapi_connection.rollback()
        finally:
            cursor.close()
            dbapi_connection.commit()


def load_sample_data(app):
    from .tests.sample_data import load_sample
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'IMPORT',
    }
    testapp = TestApp(app, environ)
    load_sample(testapp)


def load_workbook(app, workbook_filename, docsdir, test=False):
    from .loadxl import load_all
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'IMPORT',
    }
    testapp = TestApp(app, environ)
    load_all(testapp, workbook_filename, docsdir, test=test)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    secret = settings['multiauth.policy.authtkt.secret']
    # auth_tkt has no timeout set
    # cookie will still expire at browser close
    timeout = 60 * 60 * 24
    session_factory = UnencryptedCookieSessionFactoryConfig(
        secret=secret,
        timeout=timeout,
    )

    config = Configurator(
        settings=settings,
        session_factory=session_factory,
    )

    config.include('.stats')
    config.include('pyramid_tm')
    configure_engine(settings)

    # Render an HTML page to browsers and a JSON document for API clients
    config.add_renderer(None, 'encoded.renderers.PageOrJSON')
    config.add_renderer('null_renderer', 'encoded.renderers.NullRenderer')
    config.scan('encoded.renderers')
    config.include('.authentication')
    config.include('.validation')
    config.include('.predicates')
    config.include('.contentbase')
    config.include('.views')
    config.include('.persona')
    config.include('pyramid_multiauth')

    config.include(static_resources)

    if asbool(settings.get('testing', False)):
        config.include('.tests.testing_views')
        config.include(tests_js)

    app = config.make_wsgi_app()

    if asbool(settings.get('load_sample_data', False)):
        load_sample_data(app)

    workbook_filename = settings.get('load_workbook', '')

    load_test_only = asbool(settings.get('load_test_only', False))
    docsdir = settings.get('load_docsdir', None)
    if docsdir is not None:
        docsdir = [path.strip() for path in docsdir.strip().split('\n')]
    if workbook_filename:
        load_workbook(app, workbook_filename, docsdir, test=load_test_only)

    return app
