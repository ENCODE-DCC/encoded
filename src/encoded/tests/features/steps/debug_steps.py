from behave import step


@step('I debug')
def debug(context):
    import pytest
    pytest.set_trace()
    pass


@step('I fail')
def fail(context):
    assert False
