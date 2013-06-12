from behave import step
import behaving.web.steps  # NOQA


@step(u'I should see at least {count:d} elements with the css selector "{css}"')
def should_see_at_least_count_elements_with_css(context, css, count):
    element_count = len(context.browser.find_by_css(css))
    assert element_count >= count, u'Element has at least that many counts'


@step(u'I should see {count:d} elements with the css selector "{css}"')
def should_see_count_elements_with_css(context, css, count):
    element_count = len(context.browser.find_by_css(css))
    assert element_count == count, u'Found %d (expected %d)' % (element_count, count)


@step(u'I should see exactly one element with the css selector "{css}" containing the text "{text}"')
def should_see_element_with_css_and_text(context, css, text):
    elements = context.browser.find_by_css(css)
    assert len(elements) == 1
    assert elements.first.text == text


@step(u'I click the element with the css selector "{css}"')
def click_element(context, css):
    elements = context.browser.find_by_css(css)
    assert len(elements) == 1

    # Scroll element to middle of window so webdriver does not scroll the
    # element underneath the floating header.
    context.browser.execute_script("window.scrollTo(0, 0);")
    location = elements.first._element.location  # webdriver element
    size = context.browser.driver.get_window_size()
    x = location['x'] - (size['width'] / 2)
    y = location['y'] - (size['height'] / 2)
    context.browser.execute_script("window.scrollTo(%d, %d);" % (x, y))

    elements.first.click()


@step(u'I wait for the table to fully load')
def wait_for_table(context):
    assert context.browser.is_element_present_by_css("table.fully-loaded")


@step(u'I wait for the content to load')
def wait_for_content(context):
    assert context.browser.is_element_present_by_css("#content.done")


@step(u'The "{url}" section should be active')
def url_section_active(context, url):
    assert context.browser.is_element_present_by_css("#global-sections > li.active > a[href='%s']" % url)
    assert context.browser.is_element_not_present_by_css("#global-sections > li.active > a:not([href='%s'])" % url)


@step(u'the title should contain the text "{text}"')
def title_contains(context, text):
    assert text in context.browser.title
