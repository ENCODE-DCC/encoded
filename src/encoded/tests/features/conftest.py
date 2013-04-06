import pytest

pytest_plugins = 'encoded.tests.bdd'


@pytest.fixture(autouse=True)
def scenario_tx(external_tx):
    pass


# These are equivalent to the environment.py hooks
#@pytest.fixture(scope='session', autouse=True)
def before_all(request, _server, context):
    from behaving.web import environment as webenv
    webenv.before_all(context)
    context.base_url = _server.application_url

    @request.addfinalizer
    def after_all():
        webenv.after_all(context)


#@pytest.fixture(autouse=True)
def before_scenario(request, context, scenario):
    from behaving.web import environment as webenv
    webenv.before_scenario(context, scenario)

    @request.addfinalizer
    def after_scenario():
        webenv.after_scenario(context, scenario)


#@pytest.fixture(scope='subfunction', autouse=True)
def before_step(request, context, step):
    print '\n\n---------BEFORE STEP--------\n\n'

    @request.addfinalizer
    def after_step():
        print '\n\n---------AFTER STEP--------\n\n'
