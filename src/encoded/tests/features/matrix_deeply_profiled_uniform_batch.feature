@matrix
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"
        When I press "Data"
        And I click the link with text that contains "Deeply Profiled Cell Lines"
        And I wait for the content to load
        Then the title should contain the text "Deeply Profiled Cell Lines – ENCODE"
