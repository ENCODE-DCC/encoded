Feature: Biosamples

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/biosamples/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/biosamples/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/sources/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/biosamples/'])"
        And I should see an element with the css selector "#content[class='container']" within 2 seconds
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 130 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9']"
        And I should see an element with the css selector "tr[data-href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9']"

        When I click the element with the css selector "tr[data-href='/biosamples/4c1e9780-cc19-4553-b9fe-8ded24af8ff9'] td:first-child"
        Then I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "#biosample-data[class='panel data-display']"
        And I should see "ENCODE2 Project, UCSC"
        And I should see "ENCODE2-Mouse"

        When I go back
        Then I should see an element with the css selector "#content[class='container']"
        When I wait for 2 seconds
        Then I should see an element with id "collection-table"
        And I should see at least 130 elements with the css selector "table.sticky-area > tbody > tr"

        When I fill in "table-filter" with "Immortal"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/biosamples/660f6f11-b18f-4e50-b377-a76270e255cc']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/biosamples/4b9c490d-7147-42ff-aa25-9390c9d1e2bf']"
        And I should see exactly one element with the css selector "#table-count" containing the text "18"

        When I fill in "table-filter" with "Tissue"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/biosamples/aa965872-9e45-4d76-b295-bec6e4fe2517']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/biosamples/4b9c490d-7147-42ff-aa25-9390c9d1e2bf']"
        And I should see exactly one element with the css selector "#table-count" containing the text "48"

        When I fill in "table-filter" with "Primary"
        Then I should see an element with the css selector "tr[class='odd'],tr[class='even'] > a[href='/biosamples/3fd1abe6-b066-4ef4-85e6-75d867a5d448']" within 1 seconds
        And I should see an element with the css selector "tr[class='odd hidden'],tr[class='even hidden'] > a[href='/biosamples/4b9c490d-7147-42ff-aa25-9390c9d1e2bf']"
        And I should see exactly one element with the css selector "#table-count" containing the text "69"
