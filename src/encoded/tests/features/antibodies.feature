Feature: Antibodies

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/antibodies/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/antibodies/']" within 5 seconds
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/sources/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/antibodies/'])"
        And I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 100 elements with the css selector "table.sticky-area > tbody > tr"
