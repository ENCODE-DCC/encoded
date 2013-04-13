@generics @usefixtures(workbook)
Feature: Generics

    Scenario: Labs
        When I visit "/labs/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 41 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Users
        When I visit "/users/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 80 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Donors
        When I visit "/donors/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 40 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Awards
        When I visit "/awards/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 37 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Documents
        When I visit "/documents/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 30 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Treatments
        When I visit "/treatments/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 6 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

    Scenario: Constructs
        When I visit "/constructs/"
        Then I should see an element with the css selector "table.sticky-area"
        And I should see at least 5 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
