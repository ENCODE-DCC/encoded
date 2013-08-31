@targets @usefixtures(workbook)
Feature: Targets

    Scenario: Active section
        When I visit "/targets/"
        Then the "/targets/" section should be active

    Scenario: Table
        When I visit "/targets/"
        And I wait for the table to fully load

        When I fill in "q" with "human"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/targets/e310f899-8622-4aa7-8c48-8c2199dc8d15/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/targets/eb576cba-6071-4c28-bba6-3c16fdbce0c7/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "12"

    Scenario: Detail page
        When I visit "/targets/e310f899-8622-4aa7-8c48-8c2199dc8d15/"
        And I should see an element with the css selector ".view-item.type-target"

        When I click the link to "http://www.uniprot.org/uniprot/Q9H2P0"
        Then the browser's URL should contain "www.uniprot.org"
        Then I should see "Q9H2P0 (ADNP_HUMAN)"

        When I go back
        Then the browser's URL should contain "/targets/"
        And I should see an element with the css selector ".view-item.type-target"
