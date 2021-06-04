@page
Feature: Portal pages

    Scenario: Render page layout
        When I visit "/pages/homepage/"
        And I wait for the content to load
        Then I should see an element with the css selector "div.layout__block--33"

    Scenario: Override column class
        When I visit "/test-section/"
        And I wait for the content to load
        Then I should see an element with the css selector ".class_override"
