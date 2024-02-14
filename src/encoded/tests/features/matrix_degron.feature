@matrix
Feature: Matrix
    Scenario: Matrix Degron
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Protein knockdown (Degron)"
        And I wait for the content to load
        Then the title should contain the text "Protein knockdown using the auxin-inducible degron"
        And I should see at least 2 elements with the css selector "tbody > tr"
        And I should see at least 3 elements with the css selector "tr > th"
        And I should see at least 1 elements with the css selector ".matrix__populated-badge"
