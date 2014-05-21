@page @usefixtures(workbook)
Feature: Portal pages

    Scenario: Render page layout
        When I visit "/about/home/"
        And I wait for the content to load
        Then I should see 3 elements with the css selector "div.col-md-4"
        And I should see an element with the css selector ".project-info"

    Scenario: Override column class
        When I visit "/about/about/"
        And I wait for the content to load
        Then I should see an element with the css selector ".class_override"
