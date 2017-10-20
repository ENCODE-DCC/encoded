@experiments @usefixtures(workbook)
Feature: Experiments

    Scenario: Collection
        When I visit "/experiments/"
        Then I should see an element with the css selector ".view-item.type-ExperimentCollection"

    Scenario: Click through
        When I visit "/experiments/"
        And I wait for the content to load
        When I click the link to "/search/?type=Experiment&assay_slims=DNA+binding"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 19 of 19 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=Experiment&assay_title=ChIP-seq"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 19 of 19 results"
