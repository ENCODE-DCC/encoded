@Summary
Feature: Single cell
    Background:
        When I visit "/single-cell/?type=SingleCellRnaSeries&status=released"
        And I wait for the content to load
        Then the title should contain the text "Single cell – ENCODE"

    Scenario: Single cell page
        Then I should see exactly one element with the css selector ".highThroughput-tab"
        Then I should see exactly one element with the css selector ".perturbedHighThroughput-tab"
        Then I should see exactly one element with the css selector ".lowThroughput-tab"
        Then I should see exactly one element with the css selector ".series-wrapper"

    Scenario: Perturbed high throughput
        When I click the link with text that contains "Perturbed high throughput"
        Then I should see "Single cell experiments performed on pooled genetic perturbation screens."
        Then I should see "No results found"
