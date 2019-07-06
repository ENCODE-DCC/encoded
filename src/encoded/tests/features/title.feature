@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "KCE"
        When I press "Data"
        And I click the link to "/search/?type=Experiment&status=released"
        And I wait for the content to load
        Then the title should contain the text "Search – KCE"
