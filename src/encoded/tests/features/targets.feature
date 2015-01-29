@targets @usefixtures(workbook)
Feature: Targets

    Scenario: Table
        When I visit "/targets/"
        And I wait for the table to fully load

        When I fill in "q" with "sapiens"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/targets/ADNP-human/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/targets/H3K4me3-mouse/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "15"

    Scenario: Detail page
        When I visit "/targets/ADNP-human/"
        And I should see an element with the css selector ".view-item.type-target"

        When I click the link to "http://www.uniprot.org/uniprot/Q9H2P0"
        Then the browser's URL should contain "www.uniprot.org"
        Then I should see "Q9H2P0"
        And I should see "ADNP_HUMAN"

        When I go back
        Then the browser's URL should contain "/targets/"
        And I should see an element with the css selector ".view-item.type-target"
