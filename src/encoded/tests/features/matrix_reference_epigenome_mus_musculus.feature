@matrix @usefixtures(index_workbook)
Feature: Matrix
    Scenario: Matrix Reference Epigenome
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Mouse reference epigenomes"
        And I wait for the content to load
        Then the title should contain the text "Reference Epigenome Matrix – ENCODE"
        And I should see at least 4 elements with the css selector "tbody > tr"
        And I should see at least 4 elements with the css selector "tr > th"
        And I should see 0 elements with the css selector ".test-project-selector [for='all']"
        And I should see 0 elements with the css selector ".test-project-selector [for='roadmap']"
        And I should see 0 elements with the css selector ".test-project-selector [for='nonroadmap']"
        And I should see 0 elements with the css selector ".test-project-selector input[value='All'][checked]"
