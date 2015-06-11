import pytest

pytest_plugins = [
    'encoded.tests.features.browsersteps',
    'encoded.tests.features.customsteps',
]


@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, postgresql_server):
    from .. import test_indexing
    return test_indexing.app_settings(server_host_port, elasticsearch_server, postgresql_server)


@pytest.yield_fixture(scope='session')
def app(app_settings):
    from .. import test_indexing
    from contentbase.elasticsearch import create_mapping
    for app in test_indexing.app(app_settings):
        create_mapping.run(app)
        yield app


# Though this is expensive, set up first within browser tests to avoid remote
# browser timeout
@pytest.mark.fixture_cost(-1)
@pytest.yield_fixture(scope='session')
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


@pytest.fixture(scope='session')
def base_url(_server):
    return _server


@pytest.fixture(scope='session')
def splinter_browser_load_condition():

    def condition(browser):
        return browser.is_element_not_present_by_css("#application") or \
            browser.is_element_not_present_by_css(".communicating")

    return condition


@pytest.fixture(scope='session')
def splinter_driver_kwargs(request):
    return dict(request.config.option.browser_args or ())


# https://github.com/pytest-dev/pytest-bdd/issues/117


def write_line(request, when, line):
    """Write line instantly."""
    terminal = request.config.pluginmanager.getplugin('terminalreporter')
    if terminal.verbosity <= 0:
        return
    capman = request.config.pluginmanager.getplugin('capturemanager')
    out, err = capman.suspendcapture()
    try:
        request.node.add_report_section(when, 'out', out)
        request.node.add_report_section(when, 'err', err)
        terminal.write_line(line)
    finally:
        capman.resumecapture()


@pytest.mark.trylast
def pytest_bdd_before_scenario(request, feature, scenario):
    write_line(request, 'setup', u'Scenario: {scenario.name}'.format(scenario=scenario))


@pytest.mark.trylast
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    write_line(request, 'call', u'Step: {step.name} FAILED'.format(step=step))


@pytest.mark.trylast
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    write_line(request, 'call', u'Step: {step.name} PASSED'.format(step=step))
