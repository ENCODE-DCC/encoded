@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ClinGen"
        When I click the link with text that contains "Curation Central"
        And I wait for the content to load
        Then the title should contain the text "ClinGen"
