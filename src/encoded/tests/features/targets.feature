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
        And I should see at least 18 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/targets/f26cc43c-884a-4aea-9b26-b3517ef6748d']"
        When I fill in "table-filter" with "mouse"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/targets/3fef948f-34e8-412f-8ad8-8911184b131e']"
        And I should see exactly one element with the css selector "#table-count" containing the text "5"
        When I click the link to "/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
