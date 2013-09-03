@biosamples @usefixtures(workbook)
Feature: Biosamples

    Scenario: Active section
        When I visit "/biosamples/"
        Then the "/biosamples/" section should be active

    Scenario: Detail page
        When I visit "/biosamples/56e94f2b-25ac-4c58-9828-f63b66220999/"
        Then I should see "Richard Myers, HAIB"
        And I should see "ENCODE2"

    Scenario: Table
        When I visit "/biosamples/"
        And I wait for the table to fully load

        When I fill in "q" with "Immortal"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/biosamples/56e94f2b-25ac-4c58-9828-f63b66220999/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/biosamples/670715c5-9247-42ed-a94e-5b7198be75e0/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "12"

        When I fill in "q" with "Tissue"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/biosamples/670715c5-9247-42ed-a94e-5b7198be75e0/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/biosamples/56e94f2b-25ac-4c58-9828-f63b66220999/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "5"

        When I fill in "q" with "primary cell"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/biosamples/9d192023-d78e-4f24-8e58-33b5f379faba/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/biosamples/56e94f2b-25ac-4c58-9828-f63b66220999/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "4"
