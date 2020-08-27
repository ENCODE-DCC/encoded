@experiments @usefixtures(index_workbook)
Feature: Experiments

    Scenario: Collection
        When I visit "/experiments/"
        Then I should see an element with the css selector ".view-item.type-ExperimentCollection"

    Scenario: Click through
        When I visit "/experiments/"
        And I wait for the content to load
        When I click the link to "/search/?type=Experiment&assay_slims=DNA+binding"
        And I wait for 10 seconds
        Then I should see an element with the css selector "div.search-results"
        And I should see "Showing 22 of 22 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=Experiment&assay_title=TF+ChIP-seq"
        Then I should see an element with the css selector "div.search-results"
        And I should see "Showing 9 of 9 results"
