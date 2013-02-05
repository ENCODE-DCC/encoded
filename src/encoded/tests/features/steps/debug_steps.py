from behave import then


@then('I debug')
def i_debug(context):
    import pdb
    pdb.set_trace()
    pass
