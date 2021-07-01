@Summary
Feature: Encyclopedia
    Scenario: Encyclopedia
        When I visit "/encyclopedia"
        And I wait for the content to load
        Then I should see "Encyclopedia - Integrative Annotations"

        When I press "Mus musculus"
        And I wait for the content to load
        Then I should see "There are 0 files displayed out of 0 files that match the selected filters."

        When I press "Homo sapiens"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".facet-wrapper"
