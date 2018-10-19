@title
Feature: Title

    Scenario: Title updates
        When I visit "/news/"
        And I wait for the content to load
        Then the title should contain the text "/news/ – ENCODE"

@News @usefixtures(workbook)
Feature: News
    Background:
        When I visit "/news/"
        And I wait for the content to load


    Scenario: News Listing
        Then the title should contain the text "/news/"
        Then I should see at least 2 elements with the css selector "[data-test='news-facets']"
        Then I should see at least 10 elements with the css selector "[data-test='news-listing'] > div"
