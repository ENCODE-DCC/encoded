from behaving.web.steps import *


@then(u'I should see at least {count:d} elements with the css selector "{css}"')
def should_see_count_elements_with_css(context, css, count):
    assert len(context.browser.find_by_css(css)) >= count, u'Element has at least that many counts'


@then(u'I should see exactly one element with the css selector "{css}" containing the text "{text}"')
def should_see_element_with_css_and_text(context, css, text):
    elements = context.browser.find_by_css(css)
    assert len(elements) == 1
    assert elements.first.text == text


@when(u'I click the element with the css selector "{css}"')
@persona_vars
def click_element(context, css):
    elements = context.browser.find_by_css(css)
    assert len(elements) == 1
    elements.first.click()
