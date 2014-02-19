import base64
import json
import subprocess
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.settings import asbool
from sqlalchemy import engine_from_config
from webob.cookies import JSONSerializer
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
        timeout = settings.get('postgresql.statement_timeout')
        if timeout:
            timeout = int(timeout) * 1000
            set_postgresql_statement_timeout(engine, timeout)
    if test_setup:
        return engine
    if asbool(settings.get('create_tables', True)):
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


def set_postgresql_statement_timeout(engine, timeout=20 * 1000):
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


def load_ontology(config):
    settings = config.registry.settings
    path = settings.get('ontology_path')
    if path is None:
        config.registry['ontology'] = {}
        return
    config.registry['ontology'] = json.load(open(path))


def session(config):
    """ To create a session secret on the server:

    $ cat /dev/urandom | head -c 256 | base64 > session-secret.b64
    """
    settings = config.registry.settings
    if 'session.secret' in settings:
        secret = settings['session.secret'].strip()
        if secret.startswith('/'):
            secret = open(secret).read()
            secret = base64.b64decode(secret)
    else:
        secret = open('/dev/urandom').read(256)
    # auth_tkt has no timeout set
    # cookie will still expire at browser close
    if 'session.timeout' in settings:
        timeout = int(settings['session.timeout'])
    else:
        timeout = 60 * 60 * 24
    session_factory = SignedCookieSessionFactory(
        secret=secret,
        timeout=timeout,
        reissue_time=2**32,  # None does not work
        serializer=JSONSerializer(),
    )
    config.set_session_factory(session_factory)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.include(session)
    config.include('.stats')
    config.include('pyramid_tm')
    configure_engine(settings)

    # Render an HTML page to browsers and a JSON document for API clients
    config.include('.renderers')
    config.include('.authentication')
    config.include('.validation')
    config.include('.predicates')
    config.include('.contentbase')
    config.include('.indexing')
    config.include('.server_defaults')
    config.include('.views')
    config.include('.migrator')
    config.include('.auditor')

    settings = config.registry.settings
    hostname_command = settings.get('hostname_command', '').strip()
    if hostname_command:
        hostname = subprocess.check_output(hostname_command, shell=True).strip()
        settings.setdefault('persona.audiences', '')
        settings['persona.audiences'] += '\nhttp://%s' % hostname

    config.include('.persona')
    config.include('pyramid_multiauth')
    from .local_roles import LocalRolesAuthorizationPolicy
    config.set_authorization_policy(LocalRolesAuthorizationPolicy())

    config.include(static_resources)
    config.include(load_ontology)

    if asbool(settings.get('testing', False)):
        config.include('.tests.testing_views')
        config.include(tests_js)

    # Load upgrades last so that all views (including testing views) are
    # registered.
    config.include('.upgrade')
    config.include('.audit')

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
