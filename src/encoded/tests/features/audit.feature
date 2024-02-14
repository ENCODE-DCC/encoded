@title
Feature: Title

    Scenario: Title updates
        When I visit "/audit/?type=Experiment"
        And I wait for the content to load
        Then the title should contain the text "Audit – ENCODE"

@audit
Feature: Audit
    Background:
        When I visit "/audit/?type=Experiment"
        And I wait for the content to load


    Scenario: Audit
        Then the title should contain the text "Audit"
        Then I should see at least 15 elements with the css selector "tbody > tr"
        Then I should see at least 10 elements with the css selector "tr > th"
        Then I should see at least 5 elements with the css selector "div.orientation > div.facet-list-wrapper > div.facet-group"

    Scenario: Audit Buttons and Links
        Then I should see exactly one element with the css selector "[data-test='batch-download']"
        Then I should see exactly one element with the css selector "[data-test='visualize']"
        Then I should see exactly one element with the css selector "[data-test='filter-search-box']"
        Then I should see exactly one element with the css selector "[data-test='search']"
        Then I should see exactly one element with the css selector "[data-test='report']"
