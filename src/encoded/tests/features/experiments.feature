@experiments @usefixtures(workbook)
Feature: Experiments

    Scenario: Active section
        When I visit "/experiments/"
        Then the "/experiments/" section should be active

    Scenario: Table
        When I visit "/experiments/"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 9 elements with the css selector "table.sticky-area > tbody > tr"
        When I wait for the table to fully load
        Then I should see an element with the css selector "a[href='/experiments/ENCSR000AES/']"

    Scenario: Click through
        When I visit "/experiments/"
        And I wait for the table to fully load
        When I click the link to "/experiments/ENCSR000ACY/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "primary cell line"
        And I should see "ENCODE2"

        When I go back
        And I wait for the table to fully load
        When I click the link to "/experiments/ENCSR000AEN/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "ENCODE3"

    Scenario: Detail page
        When I visit "/experiments/ENCSR000AER/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "Thomas Gingeras, CSHL"
        And I should see "ENCODE3"

    Scenario: Detail page 2
        When I visit "/experiments/ENCSR000AHF/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "wgEncodeEH003317"
        And I should see "Richard Myers, HAIB"
        And I should see "ENCODE2"

    Scenario: Filter
        When I visit "/experiments/"
        And I wait for the table to fully load 
        When I fill in "q" with "Chip-seq"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/experiments/ENCSR000ADI/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/experiments/ENCSR000ACY/']"