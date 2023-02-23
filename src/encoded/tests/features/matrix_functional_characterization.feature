@matrix
Feature: Matrix
    Scenario: Functional Characterization Matrix
        When I visit "/"

        When I click the link with text that contains "Functional characterization"
        And I wait for the content to load
        Then the title should contain the text "Functional characterizations – ENCODE"
        And I should see 2 elements with the css selector ".matrix__row-category"
        And I should see at least 10 elements with the css selector "tr > th > a.header-title"
        And I should see at least 2 elements with the css selector "tr.matrix__row-data"
        And I should see an element with the css selector ".search-results__facets"
