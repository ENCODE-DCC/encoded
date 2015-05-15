from future.standard_library import install_aliases
install_aliases()
import base64
import codecs
import json
import os
try:
    import subprocess32 as subprocess  # Closes pipes on failure
except ImportError:
    import subprocess
from pyramid.config import Configurator
from pyramid.path import (
    AssetResolver,
    caller_package,
)
from pyramid.session import SignedCookieSessionFactory
from pyramid.settings import asbool
from sqlalchemy import engine_from_config
from webob.cookies import JSONSerializer
from contentbase.storage import (
    Base,
    DBSession,
)
STATIC_MAX_AGE = 0


def json_asset(spec, **kw):
    utf8 = codecs.getreader("utf-8")
    asset = AssetResolver(caller_package()).resolve(spec)
    return json.load(utf8(asset.stream()), **kw)


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


def configure_engine(settings, test_setup=False):
    from contentbase.json_renderer import json_renderer
    engine_url = settings.get('sqlalchemy.url')
    if not engine_url:
        # Already setup by test fixture
        return None
    engine_opts = {}
    if engine_url.startswith('postgresql'):
        engine_opts = dict(
            isolation_level='REPEATABLE READ',
            json_serializer=json_renderer.dumps,
        )
    engine = engine_from_config(settings, 'sqlalchemy.', **engine_opts)
    if engine.url.drivername == 'postgresql':
        timeout = settings.get('postgresql.statement_timeout')
        if timeout:
            timeout = int(timeout) * 1000
            set_postgresql_statement_timeout(engine, timeout)
    if test_setup:
        return engine
    if asbool(settings.get('create_tables', False)):
        Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return engine


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
        secret = os.urandom(256)
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


def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = global_config
    settings.update(local_config)

    settings['contentbase.jsonld.namespaces'] = json_asset('encoded:schemas/namespaces.json')
    settings['contentbase.jsonld.terms_namespace'] = 'https://www.encodeproject.org/terms/'
    settings['contentbase.jsonld.terms_prefix'] = 'encode'
    settings['contentbase.elasticsearch.index'] = 'encoded'
    hostname_command = settings.get('hostname_command', '').strip()
    if hostname_command:
        hostname = subprocess.check_output(hostname_command, shell=True).strip()
        settings.setdefault('persona.audiences', '')
        settings['persona.audiences'] += '\nhttp://%s' % hostname
        settings['persona.audiences'] += '\nhttp://%s:6543' % hostname

    config = Configurator(settings=settings)
    config.registry['app_factory'] = main  # used by mp_indexer

    config.include('pyramid_multiauth')  # must be before calling set_authorization_policy
    from pyramid_localroles import LocalRolesAuthorizationPolicy
    # Override default authz policy set by pyramid_multiauth
    config.set_authorization_policy(LocalRolesAuthorizationPolicy())
    config.include(session)
    config.include('.persona')

    configure_engine(settings)
    config.include('contentbase')
    config.commit()  # commit so search can override listing

    # Render an HTML page to browsers and a JSON document for API clients
    config.include('.renderers')
    config.include('.authentication')
    config.include('.server_defaults')
    config.include('.types')
    config.include('.root')
    config.include('.batch_download')
    config.include('.visualization')

    if 'elasticsearch.server' in config.registry.settings:
        config.include('contentbase.elasticsearch')
        config.include('.search')

    config.include(static_resources)
    config.include(load_ontology)

    if asbool(settings.get('testing', False)):
        config.include('.tests.testing_views')

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
