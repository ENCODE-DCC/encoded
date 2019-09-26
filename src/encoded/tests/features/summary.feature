@title
Feature: Title

    Scenario: Title updates
        When I visit "/summary/?type=Experiment&status=released"
        And I wait for the content to load
        Then the title should contain the text "Summary – ENCODE"

@Summary @usefixtures(workbook)
Feature: Summary
    Background:
        When I visit "/summary/?type=Experiment&status=released"
        And I wait for the content to load


    Scenario: Summary
        Then the title should contain the text "Summary"
        Then I should see at least 2 elements with the css selector ".summary-content__data > div"

    Scenario: Summary Buttons and Links
        Then I should see exactly one element with the css selector "[data-test='search']"
        Then I should see exactly one element with the css selector "[data-test='report']"
        Then I should see exactly one element with the css selector "[data-test='matrix']"
