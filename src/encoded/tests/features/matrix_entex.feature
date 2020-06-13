@matrix @usefixtures(workbook)
Feature: Matrix
    Scenario: Matrix ENTEx
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "ENTEx"
        And I wait for the content to load
        Then the title should contain the text "Epigenomes from four individuals (ENTEx) – ENCODE"
        And I should see at least 2 elements with the css selector "tbody > tr"
        And I should see at least 2 elements with the css selector "tr > th"
        And I should see at least 4 elements with the css selector ".donor-cell .donor-quadrant"
        And I should see at least 4 elements with the css selector ".donor-legend .donor-legend-row"
