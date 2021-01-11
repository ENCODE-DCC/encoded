@title
Feature: Title

    Scenario: Title updates
        When I visit "/summary/?type=Experiment&status=released"
        And I wait for the content to load
        Then the title should contain the text "Summary – ENCODE"

@Summary @usefixtures(index_workbook)
Feature: Summary
    Background:
        When I visit "/summary/?type=Experiment&status=released"
        And I wait for the content to load


    Scenario: Summary
        Then the title should contain the text "Summary"
        Then I should see at least 2 elements with the css selector ".summary-content__data > div"

    Scenario: Summary Buttons and Links
        When I click the link with text that contains "Mus musculus"
        Then I should see exactly one element with the css selector "[data-test='search']"
        Then I should see exactly one element with the css selector "[data-test='report']"
        Then I should see exactly one element with the css selector "[data-test='matrix']"
