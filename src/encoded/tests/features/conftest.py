import pytest

pytest_plugins = 'encoded.tests.bdd'


@pytest.fixture(autouse=True)
def scenario_tx(external_tx):
    pass


#@pytest.fixture(scope='session')
def browser(context, before_all):
    from behaving.web.steps.browser import given_a_browser
    # context.default_browser = 'remote'
    given_a_browser(context)


# These are equivalent to the environment.py hooks
#@pytest.fixture(scope='session', autouse=True)
def before_all(request, _server, context):
    import behaving.web
    behaving.web.setup(context)
    context.base_url = _server.application_url

    @request.addfinalizer
    def after_all():
        behaving.web.teardown(context)


#@pytest.fixture(scope='function', autouse=True)
def before_scenario(request, context, scenario):
    pass

    @request.addfinalizer
    def after_scenario():
        pass


#@pytest.fixture(scope='subfunction', autouse=True)
def before_step(request, context, step):

    @request.addfinalizer
    def after_step():
        if step.status == 'failed':
            context.browser.driver.save_screenshot('failed_step.png')
