@title
Feature: Title

    Scenario: Title updates
        When I visit "/report/?type=Experiment"
        And I wait for the content to load
        Then the title should contain the text "Report – ENCODE"

@report
Feature: Report
    Background:
        When I visit "/report/?type=Experiment"
        And I wait for the content to load
        And I wait for 15 seconds


    Scenario: Report
        Then the title should contain the text "Report"
        Then I should see at least 15 elements with the css selector "tbody > tr"
        Then I should see at least 10 elements with the css selector "tr > th"
        Then I should see at least 5 elements with the css selector "div.orientation > div.facet-list-wrapper > div.facet-group"

    Scenario: Report Buttons and Links
        Then I should see exactly one element with the css selector "[data-test='search']"
        Then I should see exactly one element with the css selector "[data-test='matrix']"
        Then I should see exactly one element with the css selector "[title='Choose columns']"
        Then I should see exactly one element with the css selector "[data-test='download-tsv']"
