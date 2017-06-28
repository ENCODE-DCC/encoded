@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"
        When I press "Data"
        And I click the link to "/search/?type=Experiment"
        And I wait for the content to load
        Then the title should contain the text "Search – ENCODE"
