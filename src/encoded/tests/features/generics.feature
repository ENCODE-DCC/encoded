Feature: Generics

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/labs/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 38 elements with the css selector "table.sticky-area > tbody > tr[data-href][data-href]"
        When I visit "/users/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 78 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
        When I visit "/donors/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 40 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
        When I visit "/awards/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 67 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
        When I visit "/submitters/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 94 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
        When I visit "/documents/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 40 elements with the css selector "table.sticky-area > tbody > tr[data-href]"
        When I visit "/biosamples/"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see at least 40 elements with the css selector "table.sticky-area > tbody > tr[data-href]"

