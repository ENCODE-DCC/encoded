@title
Feature: Title

    Scenario: Title updates
        When I visit "/audit/?type=Experiment"
        And I wait for the content to load
        Then the title should contain the text "matrix – ENCODE"

@audit @usefixtures(workbook)
Feature: Audit
    Background:
        When I visit "/audit/?type=Experiment"
        And I wait for the content to load


    Scenario: Audit
        Then the title should contain the text "matrix"
        Then I should see at least 15 elements with the css selector "tbody > tr"
        Then I should see at least 10 elements with the css selector "tr > th"
        Then I should see at least 5 elements with the css selector "div.orientation > div.facet"

    Scenario: Audit Buttons and Links
        Then I should see exactly one element with the css selector "[data-test='batch-download']"
        Then I should see exactly one element with the css selector "[data-test='visualize']"
        Then I should see exactly one element with the css selector "[data-test='filter-search-box']"
        Then I should see exactly one element with the css selector "[title='View results as list']"
        Then I should see exactly one element with the css selector "[title='View tabular report']"
