@batchhubs @usefixtures(index_workbook)
Feature: Batch Hubs
    Background:
        When I visit "/search/?type=Experiment&status=released"
        And I wait for the content to load


    Scenario: Batch Visualize
        When I press "visualize-control"
        Then I should see "Open visualization browser"
        And I should see 5 elements with the css selector ".browser-selector__assembly-option"
        And I should see 8 elements with the css selector ".browser-selector__browser"

        When I press "Close"
        Then I should not see "Open visualization browser"
