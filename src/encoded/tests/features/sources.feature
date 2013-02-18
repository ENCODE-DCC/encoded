Feature: Sources

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/sources/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/sources/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/targets/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/sources/'])"
        And I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 5 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/sources/3aa827c3-92f8-41fa-9608-201558f7a1c4']"
        When I click the link to "/sources/3aa827c3-92f8-41fa-9608-201558f7a1c4"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#souce-data[class='panel data-display'"
