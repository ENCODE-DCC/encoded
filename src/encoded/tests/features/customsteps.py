from pytest_bdd.parsers import parse
from pytest_bdd import (
    then,
    when,
)


@then(parse('the title should contain the text "{text}"'))
def the_title_should_contain_the_text(browser, text, splinter_selenium_implicit_wait):
    browser.wait_for_condition(
        lambda browser: text in browser.title,
        timeout=splinter_selenium_implicit_wait)


@then(parse('I should see at least {count:d} elements with the css selector "{css}"'))
def should_see_at_least_count_elements_with_css(browser, css, count):
    element_count = len(browser.find_by_css(css))
    assert element_count >= count, u'Element has at least that many counts'


@then(parse('I should see {count:d} elements with the css selector "{css}"'))
def should_see_count_elements_with_css(browser, css, count):
    element_count = len(browser.find_by_css(css))
    assert element_count == count, u'Found %d (expected %d)' % (element_count, count)


@then(parse('I should see exactly one element with the css selector "{css}" containing the text "{text}"'))
def should_see_element_with_css_and_text(browser, css, text):
    elements = browser.find_by_css(css)
    assert len(elements) == 1
    element_text = elements.first.text
    assert text in element_text


@when(parse('I click the element with the css selector "{css}"'))
def click_element(browser, css):
    elements = browser.find_by_css(css)
    assert len(elements) == 1

    # Scroll element to middle of window so webdriver does not scroll the
    # element underneath the floating header.
    browser.execute_script("window.scrollTo(0, 0);")
    location = elements.first._element.location  # webdriver element
    size = browser.driver.get_window_size()
    x = location['x'] - (size['width'] / 2)
    y = location['y'] - (size['height'] / 2)
    browser.execute_script("window.scrollTo(%d, %d);" % (x, y))

    elements.first.click()


@when('I wait for the table to fully load')
def wait_for_table(browser): 
    assert browser.is_element_present_by_css("table.collection-table", wait_time=15)
    assert browser.is_element_not_present_by_css("label-warning.spinner-warning", wait_time=15)


@when('I wait for deferred content to fully load')
def wait_for_fetched_content(browser):
    assert browser.is_element_present_by_css(".communicating")
    assert browser.is_element_not_present_by_css(".communicating")


@when(u'I wait for the form to fully load')
def wait_for_form(browser):
    assert browser.is_element_present_by_css("#content form")


@when(u'I wait for the content to load')
def wait_for_content(browser):
    assert browser.is_element_present_by_css("#application")
    assert browser.is_element_not_present_by_css("#application.communicating")


@when(parse('I wait for an element with the css selector "{css}" to load'))
def wait_for_css(browser, css):
    assert browser.is_element_present_by_css(css)


@then(parse('The "{url}" section should be active'))
def url_section_active(browser, url):
    assert browser.is_element_present_by_css("#global-sections > li.active > a[href='%s']" % url)
    assert browser.is_element_not_present_by_css("#global-sections > li.active > a:not([href='%s'])" % url)
