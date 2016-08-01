@page @usefixtures(workbook,admin_user)
Feature: Portal pages

    Scenario: Render page layout
        When I visit "/pages/homepage/"
        And I wait for the content to load
        Then I should see an element with the css selector "div.col-md-4"

    Scenario: Override column class
        When I visit "/test-section/"
        And I wait for the content to load
        Then I should see an element with the css selector ".class_override"

    Scenario: Add a page
        When I visit "/pages/"
        And I wait for the table to fully load
        And I press "Add"
        And I wait for the form to fully load
        And I fill in "name" with "test"
        And I fill in "title" with "Test"
        And I press "Save"
        And I wait for the content to load
        Then the browser's URL should contain "/test/"
        And the title should contain the text "Test"
