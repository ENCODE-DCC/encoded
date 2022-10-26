@matrix
Feature: Matrix
    Scenario: Mouse development matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Mouse development matrix"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".mouse-dev-matrix"
        And I should see at least 7 elements with the css selector "tbody > tr"

    Scenario: Filter by adult
        When I visit "/mouse-development-matrix/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries&replicates.library.biosample.organism.scientific_name=Mus+musculus"
        And I wait for the content to load
        Then I should see an element with id "postnatal_0_days"

        When I press "postnatal"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "tbody > tr"
