from behaving.web import environment as webenv


def before_all(context):
    context.base_url = 'http://localhost:6543/'
    webenv.before_all(context)


def after_all(context):
    webenv.after_all(context)


def before_scenario(context, scenario):
    webenv.before_scenario(context, scenario)


def after_scenario(context, scenario):
    webenv.after_scenario(context, scenario)
