import pytest
from functools import wraps
from selenium.webdriver.chrome.options import Options


pytest_plugins = [
    'encoded.tests.features.browsersteps',
    'encoded.tests.features.customsteps',
]


@pytest.fixture
def external_tx():
    pass


@pytest.fixture(scope='session')
def app_settings(wsgi_server_host_port, elasticsearch_server, postgresql_server, redis_server):
    from encoded.tests.test_indexing import _app_settings
    return _app_settings(wsgi_server_host_port, elasticsearch_server, postgresql_server, redis_server)


@pytest.yield_fixture(scope='session')
def app(app_settings):
    from encoded.tests.test_indexing import _app
    from snovault.elasticsearch import create_mapping
    for app in _app(app_settings):
        create_mapping.run(app)
        yield app


def load_once_or_yield(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.loaded:
            wrapper.loaded = True
            yield from func(*args, **kwargs)
        else:
            yield
    wrapper.loaded = False
    return wrapper


@pytest.yield_fixture(scope='session')
@load_once_or_yield
def index_workbook(request, app):
    from snovault import DBSESSION
    connection = app.registry[DBSESSION].bind.pool.unique_connection()
    connection.detach()
    conn = connection.connection
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("""TRUNCATE resources, transactions CASCADE;""")
    cursor.close()

    from webtest import TestApp
    log_level = request.config.getoption("--log")
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    from encoded.loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir, log_level=log_level)

    testapp.post_json('/index', {'is_testing_full': True})
    yield
    # XXX cleanup


@pytest.fixture(scope='session')
def wsgi_server_app(app):
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


@pytest.fixture(scope='session')
def base_url(wsgi_server):
    return wsgi_server


@pytest.fixture(scope='session')
def splinter_driver_kwargs(request):
    kwargs = dict(request.config.option.browser_args or ())
    arguments = get_chrome_webdriver_options(request)
    if arguments:
        kwargs['options'] = set_chrome_webdriver_options(arguments)
    return kwargs


@pytest.fixture(scope='session')
def splinter_window_size():
    # Sauce Labs seems to only support 1024x768.
    return (1024, 768)


# Depend on workbook fixture here to avoid remote browser timeouts.
@pytest.fixture(scope='session')
def browser(index_workbook, session_browser):
    return session_browser


@pytest.yield_fixture(scope='session')
def admin_user(browser, base_url):
    browser.visit(base_url)  # need to be on domain to set cookie
    browser.cookies.add({'REMOTE_USER': 'TEST'})
    yield
    browser.cookies.delete('REMOTE_USER')


@pytest.yield_fixture(scope='session')
def submitter_user(browser, base_url, admin_user):
    browser.visit(base_url + '/#!impersonate-user')
    browser.find_by_css('.item-picker input[type="text"]').first.fill('J. Michael Cherry')
    browser.find_by_css('.btn-primary').first.click()  # First click opens on blur, then closes
    browser.find_by_css('.btn-primary').first.click()
    browser.find_by_text('Select').first.click()
    browser.is_text_present('Submit', wait_time=10)
    browser.find_by_text('Submit').first.click()
    browser.is_text_present('J. Michael Cherry', wait_time=5)
    yield
    browser.visit(base_url + '/logout')


@pytest.fixture
def pytestbdd_strict_gherkin():
    return False


# https://github.com/pytest-dev/pytest-bdd/issues/117


def write_line(request, when, line):
    """Write line instantly."""
    terminal = request.config.pluginmanager.getplugin('terminalreporter')
    if terminal.verbosity <= 0:
        return
    capman = request.config.pluginmanager.getplugin('capturemanager')
    outerr = capman.suspend_global_capture()
    try:
        if outerr is not None:
            out, err = outerr
            request.node.add_report_section(when, 'out', out)
            request.node.add_report_section(when, 'err', err)
        terminal.write_line(line)
    finally:
        capman.resume_global_capture()


@pytest.mark.trylast
def pytest_bdd_before_scenario(request, feature, scenario):
    write_line(request, 'setup', u'Scenario: {scenario.name}'.format(scenario=scenario))


@pytest.mark.trylast
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    write_line(request, 'call', u'Step: {step.name} FAILED'.format(step=step))


@pytest.mark.trylast
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    write_line(request, 'call', u'Step: {step.name} PASSED'.format(step=step))


def get_chrome_webdriver_options(request):
    arguments = request.config.option.chrome_options or ''
    arguments = arguments.split()
    return arguments


def set_chrome_webdriver_options(arguments):
    options = Options()
    for argument in arguments:
        options.add_argument(argument)
    return options
