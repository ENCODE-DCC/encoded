@create-gene-disease
Feature: Create Gene Disease

    Scenario: See Required-Fields errors
        When I visit "/create-gene-disease/"
        And I click the element with the css selector ".btn-primary"
        Then I should see "Required"
