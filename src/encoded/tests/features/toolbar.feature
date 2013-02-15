Feature: Toolbar

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/'])"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/sources/']"
        And I should see an element with the css selector "#user-actions > li > #signin[href='#login']"
        And I should see an element with the css selector "#user-actions > li[style='display: none;'] > #signout[href='#logout']"
        And I should see "Welcome to ENCODE 3"
        When I visit "/targets/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/targets/']"
        When I visit "/antibodies/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/antibodies/']" within 5 seconds
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/antibodies/'])"
