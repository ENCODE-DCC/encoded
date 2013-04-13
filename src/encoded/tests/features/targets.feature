@targets @usefixtures(workbook)
Feature: Targets

    Scenario: Active section
        When I visit "/targets/"
        Then the "/targets/" section should be active

    Scenario: Table
        When I visit "/targets/"
        Then I should see an element with the css selector "table.sticky-area > tbody > tr"
        Then I should see at least 19 elements with the css selector "table.sticky-area > tbody > tr"

        When I wait for the table to fully load
        And I should see an element with the css selector "a[href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"
        And I should see an element with the css selector "tr[data-href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"

        When I fill in "table-filter" with "mouse"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/targets/c21f310f-fb91-4505-b62c-c8c707696827']"
        And I should see exactly one element with the css selector "#table-count" containing the text "9"


    Scenario: Click through
        When I visit "/targets/"
        And I wait for the table to fully load

        When I click the element with the css selector "tr[data-href='/targets/c21f310f-fb91-4505-b62c-c8c707696827'] td:first-child"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"


        When I go back
        And I wait for the table to fully load
        When I click the link to "/targets/c21f310f-fb91-4505-b62c-c8c707696827"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"


        When I go back
        And I wait for the table to fully load
        When I click the link to "http://www.uniprot.org/uniprot/P0C0S5"
        Then the browser's URL should contain "www.uniprot.org"
        Then I should see "P0C0S5 (H2AZ_HUMAN)"

    Scenario: Detail page
        When I visit "/targets/a1b236fc-38d5-4af5-a140-ede8bb6327c8"
        And I should see an element with the css selector "#target-data[class='panel data-display']"
        And I should see "Bing Ren, UCSD"
        And I should see "ENCODE2-Mouse"
        And I should see "R01HG003991"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"
