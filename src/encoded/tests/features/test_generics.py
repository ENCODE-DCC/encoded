import pytest
from pytest_bdd import (
    scenarios,
    then,
    when,
)
from . import browsersteps

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]

scenarios('generics.feature', strict_gherkin=False)


# https://github.com/pytest-dev/pytest-bdd/issues/124


@when('I visit "/<type_name>/"')
def i_visit_the_collection_for_type_name(browser, base_url, type_name):
    url = '/{}/'.format(type_name)
    browsersteps.when_i_visit_url(browser, base_url, url)


@when('I click the link with text that contains "<link_text>"')
def click_link_with_text_that_contains_link_text(browser, link_text):
    browsersteps.click_link_with_text_that_contains(browser, link_text)


@then('I should see an element with the css selector ".view-item.type-<type_name>"')
def should_see_element_with_css_type_name(browser, type_name):
    css = ".view-item.type-{}".format(type_name)
    browsersteps.should_see_element_with_css(browser, css)
