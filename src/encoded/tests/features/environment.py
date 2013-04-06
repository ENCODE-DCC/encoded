from behaving.web import environment as webenv
import pytest


def before_all(context):
    webenv.before_all(context)
    _server = pytest.bdd.getfixture('_server')
    context.base_url = _server.application_url


def after_all(context):
    webenv.after_all(context)


def before_scenario(context, scenario):
    webenv.before_scenario(context, scenario)


def after_scenario(context, scenario):
    webenv.after_scenario(context, scenario)
