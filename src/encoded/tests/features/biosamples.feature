@biosamples @usefixtures(workbook)
Feature: Biosamples

    Scenario: Active section
        When I visit "/biosamples/"
        Then the "/biosamples/" section should be active

    Scenario: Click through
        When I visit "/biosamples/"
        And I wait for the table to fully load
        When I click the element with the css selector "tr[data-href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9'] td:first-child"
        Then the browser's URL should be "/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9"
        And I should see an element with the css selector "#biosample-data[class='panel data-display']"
        And I should see "ENCODE2 Project, UCSC"
        And I should see "ENCODE2-Mouse"

        When I go back
        Then the browser's URL should be "/biosamples/"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"

    Scenario: Table
        When I visit "/biosamples/"
        Then I should see an element with the css selector "table.sticky-area > tbody > tr"

        When I wait for the table to fully load
        Then I should see at least 130 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9']"
        And I should see an element with the css selector "tr[data-href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9']"

        When I fill in "table-filter" with "Immortal"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/biosamples/6b9a8e74-1d0b-413e-9015-87d519805515']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/biosamples/aa965872-9e45-4d76-b295-bec6e4fe2517']"
        And I should see exactly one element with the css selector "#table-count" containing the text "24"

        When I fill in "table-filter" with "Tissue"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/biosamples/aa965872-9e45-4d76-b295-bec6e4fe2517']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/biosamples/6b9a8e74-1d0b-413e-9015-87d519805515']"
        And I should see exactly one element with the css selector "#table-count" containing the text "48"

        When I fill in "table-filter" with "Primary"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/biosamples/3fd1abe6-b066-4ef4-85e6-75d867a5d448']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/biosamples/6b9a8e74-1d0b-413e-9015-87d519805515']"
        And I should see exactly one element with the css selector "#table-count" containing the text "66"
