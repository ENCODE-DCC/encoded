@matrix
Feature: Matrix
    Scenario: Brain Matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Rush Alzheimer’s Disease Study"
        And I wait for the content to load
        Then the title should contain the text "Rush Alzheimer’s Disease Study – ENCODE"
        And I should see at least 2 elements with the css selector "tbody > tr"
        And I should see at least 1 elements with the css selector "tr > th"

    Scenario: Legend
        And I should see exactly 1 elements with the css selector ".brain-legend > div"
        And I should see exactly 2 elements with the css selector ".brain-legend"
        And I should see exactly 3 elements with the css selector ".brain-legend :first-child > div"
        And I should see exactly 1 elements with the css selector ".brain-legend :first-child > p"
        And I should see exactly 5 elements with the css selector ".brain-legend > div:nth-child(2) > div"
        And I should see exactly 1 elements with the css selector ".brain-legend > div:nth-child(2) > p"
        And I should see at least 1 elements with the css selector ".matrix__col-category-header > th"

    Scenario Data
        And I should see at least 1 elements with the css selector "tr.matrix__row-data"
