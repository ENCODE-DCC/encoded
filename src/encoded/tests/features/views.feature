@views @usefixtures(index_workbook)
Feature: Views
    Background:
        When I visit "/search/?type=Experiment&status=released&assay_slims=DNA+methylation"
        And I wait for the content to load


    Scenario: Search Views
        Then I should see 2 elements with the css selector ".btn-attached a"
        And I should see exactly one element with the css selector "[data-test='matrix']"
        And I should see exactly one element with the css selector "[data-test='report']"

    Scenario: Search to Matrix
        When I click the link to "/matrix/?type=Experiment&status=released&assay_slims=DNA+methylation"
        Then I should see "Showing 6 results"
        And I should see 2 elements with the css selector ".btn-attached a"
        And I should see exactly one element with the css selector "[data-test='search']"
        And I should see exactly one element with the css selector "[data-test='report']"

        When I click the link to "/matrix/?type=Experiment"
        Then I should see "Showing 69 results"

        When I click the link to "/report/?type=Experiment"
        Then I should see "Experiment report"
        And I should see 2 elements with the css selector ".btn-attached a"
        And I should see exactly one element with the css selector "[data-test='search']"
        And I should see exactly one element with the css selector "[data-test='matrix']"
