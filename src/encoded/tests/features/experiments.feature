@experiments @usefixtures(workbook)
Feature: Experiments

    Scenario: Active section
        When I visit "/experiments/"
        Then the "/experiments/" section should be active

    Scenario: Table
        When I visit "/experiments/"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 15 elements with the css selector "table.sticky-area > tbody > tr"
        When I wait for the table to fully load
        Then I should see an element with the css selector "a[href='/experiments/2219c0f3-8ad4-441e-9c42-3acd9ddffdf1']"

        When I fill in "table-filter" with "Chip-seq"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/experiments/c05a9d79-713e-4d54-8d8e-6daae94368b3']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/experiments/b1316997-1d21-493e-ed9d-6418542bc5c6']"
        And I should see exactly one element with the css selector "#table-count" containing the text "20"

    Scenario: Click through
        When I visit "/experiments/"
        And I wait for the table to fully load
        When I click the link to "/experiments/188548dc-9d9d-4928-edf5-bde05768cb42"
        Then I should see an element with the css selector "div.data-display"
        And I should see "Tissue"

        When I go back
        And I wait for the table to fully load
        When I click the link to "/experiments/d312ff9f-c684-4bd8-daf4-1fb26491e491"
        And I should see an element with the css selector "div.data-display"
        And I should see "ENCODE2-mouse"
        And I should see "Immortalized cell line"

    Scenario: Detail page
        When I visit "/experiments/8f44415a-f590-49f7-9199-b5c6ab648e14"
        Then I should see an element with the css selector "div.data-display"
        And I should see "fibroblast of lung"
        And I should see at least 1 elements with the css selector "section"
        And I should see "wgEncodeEH002199"
        And I should see "ENCODE2"

    Scenario: Detail page 2
        When I visit "/experiments/6f9ced49-d35a-4e6c-93e1-8be9c223ed1e"
        And I should see an element with the css selector "div.data-display"
        And I should see "Generalized Methods for the SYDH Histone experiments in mouse."
        And I should see "ENCFF001NBG"
        And I should see "ENCFF001NBE"