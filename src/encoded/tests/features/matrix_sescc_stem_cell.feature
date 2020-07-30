@matrix @usefixtures(workbook)
Feature: Matrix
    Scenario: SESCC-Stem-Cell-Matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Stem Cell Development Matrix (SESCC)"
        And I wait for the content to load
        Then the title should contain the text "Stem Cell Development Matrix (SESCC)"

