import pytest
from pytest_bdd import (
    scenarios,
    then,
    when,
)
from . import browsersteps

pytestmark = pytest.mark.usefixtures('workbook')

scenarios('generics.feature')


# https://github.com/pytest-dev/pytest-bdd/issues/124


@when('I visit "/<item_type>/"')
def i_visit_the_collection_for_item_type(browser, base_url, item_type):
    url = '/{}/'.format(item_type)
    browsersteps.when_i_visit_url(browser, base_url, url)


@when('I click the link with text that contains "<link_text>"')
def click_link_with_text_that_contains_link_text(browser, link_text):
    browsersteps.click_link_with_text_that_contains(browser, link_text)


@then('I should see an element with the css selector ".view-item.type-<item_type>"')
def should_see_element_with_css_item_type(browser, item_type):
    css = ".view-item.type-{}".format(item_type)
    browsersteps.should_see_element_with_css(browser, css)
