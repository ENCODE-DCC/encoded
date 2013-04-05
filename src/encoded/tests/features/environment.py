from behaving.web import environment as webenv
import pytest


@pytest.bdd.before_all
def before_all(context):
    webenv.before_all(context)
    server = pytest.bdd.getfixture('_server')
    context.base_url = server.application_url


@pytest.bdd.after_all
def after_all(context):
    webenv.after_all(context)


@pytest.bdd.before_scenario
def before_scenario(context, scenario):
    pytest.bdd.getfixture('external_tx')
    webenv.before_scenario(context, scenario)


@pytest.bdd.after_scenario
def after_scenario(context, scenario):
    webenv.after_scenario(context, scenario)
