@advanced_query_search
Feature: Search
    Background:
        When I visit "/search"
        And I wait for the content to load


    Scenario: Search
        Then the title should contain the text "Search"


    Scenario: Test advanced query search type
    When I visit "/search/?advancedQuery=@type:Experiment"
    And I wait for the content to load
    Then I should see at least 25 elements with the css selector "ul.result-table > li"


    Scenario: Test advanced query search date search
    When I visit "/search/?advancedQuery=@type:Experiment date_submitted:[2015-01-01 TO 2019-12-31]"
    And I wait for the content to load
    Then I should see at least 25 elements with the css selector "ul.result-table > li"
