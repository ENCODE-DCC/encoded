import pytest

pytest_plugins = 'encoded.tests.bdd'


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
@pytest.fixture(scope='session', autouse=True)
def before_all(request, _server, context):
    import behaving.web
    behaving.web.setup(context)
    context.base_url = _server

    @request.addfinalizer
    def after_all():
        behaving.web.teardown(context)


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
