import pytest

pytest_plugins = 'encoded.tests.bdd'


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def postgresql_server():
    from urllib import quote
    from ..postgresql_fixture import server_process
    tmpdir = str(pytest.ensuretemp('postgresql'))
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
def elasticsearch_server(elasticsearch_host_port):
    from ..elasticsearch_fixture import server_process
    host, port = elasticsearch_host_port
    tmpdir = pytest.ensuretemp('elasticsearch')
    process = server_process(str(tmpdir), host=host, port=port)

    yield 'http://%s:%d' % (host, port)

    if process.poll() is None:
        process.terminate()
        process.wait()


@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, postgresql_server):
    from ..conftest import _app_settings
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % server_host_port
    settings['elasticsearch.server'] = elasticsearch_server
    settings['sqlalchemy.url'] = postgresql_server
    settings['collection_source'] = 'elasticsearch'
    return settings


@pytest.fixture(scope='session')
def app(request, app_settings):
    '''WSGI application level functional testing.
    '''
    from encoded.storage import DBSession

    DBSession.remove()
    DBSession.configure(bind=None)

    from encoded import main
    app = main({}, **app_settings)

    from encoded.commands import create_mapping
    create_mapping.run(app)

    @request.addfinalizer
    def teardown_app():
        # Dispose connections so postgres can tear down
        DBSession.bind.pool.dispose()
        DBSession.remove()
        DBSession.configure(bind=None)

    return app


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

        from ...loadxl import load_all
        from pkg_resources import resource_filename
        inserts = resource_filename('encoded', 'tests/data/inserts/')
        docsdir = [resource_filename('encoded', 'tests/data/documents/')]
        load_all(testapp, inserts, docsdir)
        from encoded.commands import es_index_data
        es_index_data.run(app)

        yield
    finally:
        tx.rollback()


@pytest.fixture(autouse=True)
def scenario_tx(external_tx):
    pass


@pytest.fixture(scope='session', autouse=True)
def set_webdriver(request, context):
    context.default_browser = request.config.option.browser
    context.remote_webdriver = request.config.option.remote_webdriver
    context.browser_args = dict(request.config.option.browser_args or ())


@pytest.fixture(scope='session', autouse=True)
def browser(context, before_all, set_webdriver):
    from behaving.web.steps.browser import given_a_browser
    # context.default_browser = 'remote'
    given_a_browser(context)
    context.browser.driver.set_window_size(1024, 768)


# These are equivalent to the environment.py hooks
@pytest.mark.fixture_cost(1000)
@pytest.fixture(scope='session', autouse=True)
def before_all(request, _server, context):
    import behaving.web
    behaving.web.setup(context)
    context.base_url = _server
    from selenium.common.exceptions import WebDriverException

    @request.addfinalizer
    def after_all():
        try:
            behaving.web.teardown(context)
        except WebDriverException:
            pass  # remote webdriver may already have gone away


#@pytest.fixture(scope='function', autouse=True)
def before_scenario(request, context, scenario):
    pass

    @request.addfinalizer
    def after_scenario():
        pass


@pytest.fixture(scope='subfunction', autouse=True)
def before_step(request, context, step):

    @request.addfinalizer
    def after_step():
        import textwrap
        if step.status != 'failed':
            return
        print('')
        print("=" * 70)
        print("  Screenshot URL: %s" % context.browser.url)
        print("-" * 70)
        screenshot = context.browser.driver.get_screenshot_as_base64()
        print '\n'.join(textwrap.wrap('data:image/png;base64,' + screenshot))
        print("=" * 70)
