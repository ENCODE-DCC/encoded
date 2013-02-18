Feature: Targets

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/targets/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/sources/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/targets/'])"
        And I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 100 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8']"
        When I click the link to "/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
