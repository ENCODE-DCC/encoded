@platforms @usefixtures(workbook)
Feature: Platforms

    Scenario: Table
        When I visit "/platforms/"
        Then I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 5 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 5 elements with the css selector "tr > td > a"

        When I wait for the table to fully load
        And I should see exactly one element with the css selector "#table-count" containing the text "11"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"
