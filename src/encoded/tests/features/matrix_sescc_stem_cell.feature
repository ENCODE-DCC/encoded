@matrix @usefixtures(workbook)
Feature: Matrix
    Scenario: SESCC-Stem-Cell-Matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "SESCC stem cell development matrix"
        And I wait for the content to load
        Then the title should contain the text "SESCC Stem Cell Development Matrix"

