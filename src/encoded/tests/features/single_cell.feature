@title
Feature: Title

    Scenario: Title updates
        When I visit "/single-cell"
        And I wait for the content to load
        Then the title should contain the text "Single cell – ENCODE"

@Summary
Feature: Single cell
    Background:
        When I visit "/single-cell/?type=Experiment&assay_slims=Single+cell&status!=replaced"
        And I wait for the content to load

    Scenario: Single cell page
        Then I should see exactly one element with the css selector ".highThroughput-tab"
        Then I should see exactly one element with the css selector ".perturbedHighThroughput-tab"
        Then I should see exactly one element with the css selector ".lowThroughput-tab"
        Then I should see exactly one element with the css selector ".series-wrapper"

    Scenario: Peturbed high throughput
        When I click the link with text that contains "Perturbed high throughput"
        Then I should see "Single cell experiments performed on pooled genetic perturbation screens."
        Then I should see "No results found"

    Scenario: Low throughput
        When I click the link with text that contains "Low throughput"
        And I wait for the content to load
        Then I should see "Showing 2 of 2 results"
        Then I should see exactly one element with the css selector ".tab-description"
