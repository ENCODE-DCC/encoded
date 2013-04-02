from behaving.web import environment as webenv
import pytest


@pytest.behave.before_all
def before_all(context):
    webenv.before_all(context)
    server = pytest.behave.getfixture('_server')
    pytest.behave.getfixture('testdata')
    context.base_url = server.application_url


@pytest.behave.after_all
def after_all(context):
    webenv.after_all(context)


@pytest.behave.before_scenario
def before_scenario(context, scenario):
    pytest.behave.getfixture('external_tx')
    webenv.before_scenario(context, scenario)


@pytest.behave.after_scenario
def after_scenario(context, scenario):
    webenv.after_scenario(context, scenario)
