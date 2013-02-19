from behaving.web.steps import *


@then(u'I should see at least {count:d} elements with the css selector "{css}"')
def should_see_count_elements_with_css(context, css, count):
    assert len(context.browser.find_by_css(css)) >= count, u'Element has at least that many counts'
