@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"
        When I click the link to "/antibodies/"
        And I wait for the content to load
        Then the title should contain the text "Antibody Approvals – ENCODE"
