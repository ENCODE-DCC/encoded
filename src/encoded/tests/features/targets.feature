Feature: Targets

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/targets/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/sources/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/targets/'])"
        And I should see an element with the css selector "#content[class='container']" within 3 seconds
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 12 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"
        And I should see an element with the css selector "tr[data-href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"

        When I click the element with the css selector "tr[data-href='/targets/c21f310f-fb91-4505-b62c-c8c707696827'] td:first-child"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#target-data[class='panel data-display']"

        When I go back
        Then I should see an element with the css selector "#content[class='container']" within 3 seconds
        And I should see an element with id "collection-table"
        When I click the link to "/targets/c21f310f-fb91-4505-b62c-c8c707696827"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#target-data[class='panel data-display']"

        When I go back
        Then I should see an element with the css selector "#content[class='container']" within 3 seconds
        And I should see an element with id "collection-table"
        And I should see at least 19 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='http://www.uniprot.org/uniprot/P0C0S5']"

        When I click the link to "http://www.uniprot.org/uniprot/P0C0S5"
        Then I should see "P0C0S5 (H2AZ_HUMAN)"

        When I go back
        Then I should see an element with the css selector "#content[class='container']" within 3 seconds
        And I should see an element with id "collection-table"
        And I should see at least 19 elements with the css selector "table.sticky-area > tbody > tr"

        When I fill in "table-filter" with "mouse"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"
        And I should see exactly one element with the css selector "#table-count" containing the text "8"

        When I click the link to "/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
        And I should see ". Ren / Bing Ren, UCSD / ENCODE2-Mouse"