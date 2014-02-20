@search @usefixtures(workbook)
Feature: Search

    Scenario: Search
        When I visit "/search"
        And I wait for the content to load
        Then the title should contain the text "Search"

    Scenario: Search Antibodies
        When I click the link to "/search/?type=antibody_approval"
        And I wait for the content to load
        Then I should see an element with the css selector "div.facet"

    Scenario: Search Biosamples
        When I click the link to "/search/?type=biosample"
        And I wait for the content to load
        Then I should see an element with the css selector "div.facet"

    Scenario: Search Experiments
        When I click the link to "/search/?type=experiment"
        And I wait for the content to load
        Then I should see an element with the css selector "div.facet"

    Scenario: Search Targets
        When I click the link to "/search/?type=target"
        And I wait for the content to load
        Then I should see an element with the css selector "div.facet"
