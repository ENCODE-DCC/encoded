@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "Snowflakes... By SnoVault"
        When I click the link with text that contains "Data"
        And I click the link to "/search/?type=Snowfort"
        And I wait for the content to load
        Then the title should contain the text "Search – SNOWFLAKES"
