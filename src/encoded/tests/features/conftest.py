import pytest

pytest_plugins = 'encoded.tests.bdd'


@pytest.mark.fixture_lock('encoded.storage.DBSession')
@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, postgresql_server):
    from .. import test_indexing
    return test_indexing.app_settings(server_host_port, elasticsearch_server, postgresql_server)


@pytest.yield_fixture(scope='session')
def app(app_settings):
    from .. import test_indexing
    from encoded.commands import create_mapping
    for app in test_indexing.app(app_settings):
        create_mapping.run(app)
        yield app


# Though this is expensive, set up first within browser tests to avoid remote
# browser timeout
# XXX Ideally this wouldn't be autouse...
@pytest.mark.fixture_cost(-1)
@pytest.yield_fixture(scope='session', autouse=True)
def workbook(app):
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

    testapp.post_json('/index', {})
    yield
    # XXX cleanup


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
