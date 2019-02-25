""" Library of splinter browser steps.

Adapted for pytest-bdd and pytest-splinter from behaving_ 1.1.

.. _behaving: https://pypi.python.org/pypi/behaving
"""

from pytest_bdd.parsers import parse
from pytest_bdd import (
    given,
    then,
    when,
)

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


####################
# basic


@when(parse('I wait for {timeout:d} seconds'))
def wait_for_timeout(browser, timeout):
    import time
    time.sleep(timeout)


@when(parse('I show the element with id "{id}"'))
def show_element_by_id(browser, id):
    assert browser.find_by_id(id)
    browser.execute_script('document.getElementById("%s").style.display="inline";' % id)


@when(parse('I hide the element with id "{id}"'))
def hide_element_by_id(browser, id):
    assert browser.find_by_id(id)
    browser.execute_script('document.getElementById("%s").style.display="none";' % id)


@then(parse('I should see "{text}"'))
def should_see(browser, text):
    assert browser.is_text_present(text), u'Text not found'


@then(parse('I should not see "{text}"'))
def should_not_see(browser, text):
    assert browser.is_text_not_present(text), u'Text was found'


@then(parse('I should see "{text}" within {timeout:d} seconds'))
def should_see_within_timeout(browser, text, timeout):
    assert browser.is_text_present(text, wait_time=timeout), u'Text not found'


@then(parse('I should not see "{text}" within {timeout:d} seconds'))
def should_not_see_within_timeout(browser, text, timeout):
    assert browser.is_text_not_present(text, wait_time=timeout), u'Text was found'


@then(parse('I should see an element with id "{id}"'))
def should_see_element_with_id(browser, id):
    assert browser.is_element_present_by_id(id), u'Element not found'


@then(parse('I should not see an element with id "{id}"'))
def should_not_see_element_with_id(browser, id):
    assert browser.is_element_not_present_by_id(id), u'Element was found'


@then(parse('I should see an element with id "{id}" within {timeout:d} seconds'))
def should_see_element_with_id_within_timeout(browser, id, timeout):
    assert browser.is_element_present_by_id(id, wait_time=timeout), u'Element not found'


@then(parse('I should not see an element with id "{id}" within {timeout:d} seconds'))
def should_not_see_element_with_id_within_timeout(browser, id, timeout):
    assert browser.is_element_not_present_by_id(id, wait_time=timeout), u'Element was found'


@then(parse('I should see an element with the css selector "{css}"'))
def should_see_element_with_css(browser, css):
    assert browser.is_element_present_by_css(css), u'Element not found'


@then(parse('I should not see an element with the css selector "{css}"'))
def should_not_see_element_with_css(browser, css):
    assert browser.is_element_not_present_by_css(css), u'Element was found'


@then(parse('I should see an element with the css selector "{css}" within {timeout:d} seconds'))
def should_see_element_with_css_within_timeout(browser, css, timeout):
    assert browser.is_element_present_by_css(css, wait_time=timeout), u'Element not found'


@then(parse('I should not see an element with the css selector "{css}" within {timeout:d} seconds'))
def should_not_see_element_with_css_within_timeout(browser, css, timeout):
    assert browser.is_element_not_present_by_css(css, wait_time=timeout), u'Element was found'


@then(parse('I should see {n:d} elements with the css selector "{css}"'))
def should_see_n_elements_with_css(browser, n, css):
    element_list = browser.find_by_css(css)
    list_length = len(element_list)
    assert list_length == n, u'Found {list_length} elements, expected {n}'.format(**locals())


####################
# browser


@when('I reload')
def reload(browser):
    browser.reload()


@when('I go back')
def go_back(browser):
    browser.back()


@when('I go forward')
def go_forward(browser):
    browser.forward()


@when(parse('I set the cookie "{key}" to "{value}"'))
def set_cookie(browser, key, value):
    browser.cookies.add({key: value})


@when(parse('I delete the cookie "{key}"'))
def delete_cookie(browser, key):
    browser.cookies.delete(key)


@when(parse('I delete all cookies'))
def delete_all_cookies(browser):
    browser.cookies.delete()


@when(parse('I resize the browser to {width}x{height}'))
def resize_browser(browser, width, height):
    browser.driver.set_window_size(int(width), int(height))


@when(parse('I resize the viewport to {width}x{height}'))
def resize_viewport(browser, width, height):
    width = int(width)
    height = int(height)

    b_size = browser.driver.get_window_size()
    b_width = b_size['width']
    b_height = b_size['height']
    v_width = browser.evaluate_script("document.documentElement.clientWidth")
    v_height = browser.evaluate_script("document.documentElement.clientHeight")

    browser.driver.set_window_size(
        b_width + width - v_width,
        b_height + height - v_height)


@when("I maximize the browser's window")
def maximize_window(browser):
    browser.driver.maximize_window()


####################
# forms


@when(parse('I fill in "{name}" with "{value}"'))
def i_fill_in_field(browser, name, value):
    browser.fill(name, value)


@when(parse('I clear field "{name}"'))
def i_clear_field(browser, name):
    el = browser.find_element_by_name(name)
    assert el, 'Element not found'
    el.clear()


@when(parse('I type "{value}" to "{name}"'))
def i_type_to(browser, name, value):
    for key in browser.type(name, value, slowly=True):
        assert key


@when(parse('I choose "{value}" from "{name}"'))
def i_choose_in_radio(browser, name, value):
    browser.choose(name, value)


@when(parse('I check "{name}"'))
def i_check(browser, name):
    browser.check(name)


@when(parse('I uncheck "{name}"'))
def i_uncheck(browser, name):
    browser.uncheck(name)


@when(parse('I toggle "{name}"'))
def i_toggle(browser, name):
    el = browser.find_by_name('digest')
    assert el, u'Element not found'
    el = el.first
    if el.checked:
        el.uncheck()
    else:
        el.check()


@when(parse('I select "{value}" from "{name}"'))
def i_select(browser, value, name):
    from splinter.exceptions import ElementDoesNotExist
    try:
        browser.select(name, value)
    except ElementDoesNotExist:
        inp = browser.find_by_xpath("//input[@name='%s'][@value='%s']" % (name, value))
        assert inp, u'Element not found'
        inp.first.check()


@when(parse('I press "{name}"'))
def i_press(browser, name):
    element = browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']|"
         "//button[contains(text(), '%(name)s')]|"
         "//a[contains(text(), '%(name)s')]") % {'name': name})
    assert element, u'Element not found'
    element.first.click()


@when(parse('I press the element with xpath "{xpath}"'))
def i_press_xpath(browser, xpath):
    button = browser.find_by_xpath(xpath)
    assert button, u'Element not found'
    button.first.click()


@when(parse('I attach the file "{path}" to "{name}"'))
def i_attach(browser, name, path):
    import os
    if not os.path.exists(path):
        path = os.path.join(browser.attachment_dir, path)
        if not os.path.exists(path):
            assert False
    browser.attach_file(name, path)


@when(parse('I set the inner HTML of the element with id "{id}" to "{contents}"'))
def set_html_content_to_element_with_id(browser, id, contents):
    assert browser.evaluate_script("document.getElementById('%s').innerHTML = '%s'" % (id, contents)), \
        u'Element not found or could not set HTML content'


@when(parse('I set the inner HTML of the element with class "{klass}" to "{contents}"'))
def set_html_content_to_element_with_class(browser, klass, contents):
    assert browser.evaluate_script("document.getElementsByClassName('%s')[0].innerHTML = '%s'" % (klass, contents)), \
        u'Element not found or could not set HTML content'


@then(parse('field "{name}" should have the value "{value}"'))
def field_has_value(browser, name, value):
    el = browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert el.first.value == value, "Values do not match, expected %s but got %s" % (value, el.first.value)


@then(parse('"{name}" should be enabled'))
def is_enabled(browser, name):
    el = browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert el.first._element.is_enabled()


@then(parse('"{name}" should be disabled'))
@then(parse('"{name}" should not be enabled'))
def is_disabled(browser, name):
    el = browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert not el.first._element.is_enabled()


@then(parse('field "{name}" should be valid'))
def field_is_valid(browser, name):
    assert browser.find_by_name(name), u'Element not found'
    assert browser.evaluate_script("document.getElementsByName('%s')[0].checkValidity()" % name), \
        'Field is invalid'


@then(parse('field "{name}" should be invalid'))
@then(parse('field "{name}" should not be valid'))
def field_is_invalid(browser, name):
    assert browser.find_by_name(name), u'Element not found'
    assert not browser.evaluate_script("document.getElementsByName('%s')[0].checkValidity()" % name), \
        'Field is valid'


@then(parse('field "{name}" should be required'))
def field_is_required(browser, name):
    assert browser.find_by_name(name), u'Element not found'
    assert browser.evaluate_script("document.getElementsByName('%s')[0].getAttribute('required')" % name), \
        'Field is not required'


@then(parse('field "{name}" should not be required'))
def field_is_not_required(browser, name):
    assert browser.find_by_name(name), u'Element not found'
    assert not browser.evaluate_script("document.getElementsByName('%s')[0].getAttribute('required')" % name), \
        'Field is required'


@when(parse('I enter "{text}" to the alert'))
def set_alert_text(browser, text):
    alert = browser.driver.switch_to.alert
    assert alert, u'Alert not found'
    alert.send_keys(text)


@when(parse('I accept the alert'))
def accept_alert(browser):
    alert = browser.driver.switch_to.alert
    assert alert, u'Alert not found'
    alert.accept()


@when(parse('I dismiss the alert'))
def dimiss_alert(browser):
    alert = browser.driver.switch_to.alert
    assert alert, u'Alert not found'
    alert.dismiss()


####################
# links


@when(parse('I click the link to "{url}"'))
def click_link_to_url(browser, url):
    browser.click_link_by_href(url)


@when(parse('I click the link to a url that contains "{url}"'))
def click_link_to_url_that_contains(browser, url):
    browser.click_link_by_partial_href(url)


@when(parse('I click the link with text "{text}"'))
def click_link_with_text(browser, text):
    browser.click_link_by_text(text)


@when(parse('I click the link with text that contains "{text}"'))
def click_link_with_text_that_contains(browser, text):
    anchors = browser.find_link_by_partial_text(text)
    assert anchors, 'Link not found'
    anchors[0].click()


####################
# url


@given(parse('the base url "{url}"'))
def base_url(url):
    return url


@when(parse('I visit "{url}"'))
@when(parse('I go to "{url}"'))
def when_i_visit_url(browser, base_url, url):
    full_url = urljoin(base_url, url)
    browser.visit(full_url)


@then(parse('the browser\'s URL should be "{url}"'))
def the_browser_url_should_be(browser, base_url, url):
    full_url = urljoin(base_url, url)
    assert browser.url.strip() == full_url


@then(parse('the browser\'s URL should contain "{text}"'))
def the_browser_url_should_contain(browser, text):
    assert text in browser.url


@then(parse('the browser\'s URL should not contain "{text}"'))
def the_browser_url_should_not_contain(browser, text):
    assert text not in browser.url
