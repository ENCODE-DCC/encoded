import pytest

pytest_plugins = 'encoded.tests.bdd'


@pytest.mark.fixture_cost(10)
@pytest.yield_fixture(scope='session')
def postgresql_server():
    from .. import test_indexing
    for fixture in test_indexing.postgresql_server():
        yield fixture


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
    from .. import test_indexing
    return test_indexing.app_settings(server_host_port, elasticsearch_server, postgresql_server)


@pytest.fixture(scope='session')
def app(request, app_settings):
    from .. import test_indexing
    return test_indexing.app(request, app_settings)


# Though this is expensive, set up first within browser tests to avoid remote
# browser timeout
@pytest.mark.fixture_cost(-1)
@pytest.yield_fixture(scope='session')
def workbook(connection, app, app_settings):
    from .. import conftest
    from encoded.commands import es_index_data
    for fixture in conftest.workbook(connection, app, app_settings):
        es_index_data.run(app)
        yield fixture


@pytest.fixture(autouse=True)
def scenario_tx(external_tx):
    pass


@pytest.fixture(scope='session', autouse=True)
def set_webdriver(request, context):
    context.default_browser = request.config.option.browser
    context.remote_webdriver = request.config.option.remote_webdriver
    context.browser_args = dict(request.config.option.browser_args or ())


@pytest.mark.fixture_cost(1000)
@pytest.fixture(scope='session', autouse=True)
def browser(context, before_all, set_webdriver):
    from behaving.web.steps.browser import given_a_browser
    # context.default_browser = 'remote'
    given_a_browser(context)
    context.browser.driver.set_window_size(1024, 768)


# These are equivalent to the environment.py hooks
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
