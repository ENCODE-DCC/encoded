@search @usefixtures(workbook)
Feature: Search
    Background:
        When I visit "/search"
        And I wait for the content to load


    Scenario: Search
        Then the title should contain the text "Search"


    Scenario: Search Snowballs
        When I click the link with text that contains "Data"
        And I click the link to "/search/?type=Snowball"
        And I wait for the content to load
        Then I should see at least 13 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 3 elements with the css selector "div.box.facets > div.facet"

        When I click the link to "?type=Snowball&method=hand-packed"
        And I wait for the content to load
        Then I should see at least 3 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=Snowball&method=hand-packed&method=scoop-formed"
        And I wait for the content to load
        Then I should see at least 5 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search BoxI
        When I fill in "searchTerm" with "hand-packed"
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"

