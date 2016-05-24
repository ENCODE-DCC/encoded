@antibodies @usefixtures(workbook)
Feature: Antibodies

    Scenario: Table
        When I visit "/antibodies/"
        And I wait for the table to fully load

        When I fill in "q" with "Sigma"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/antibodies/ENCAB000ACQ/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/antibodies/ENCAB000AFR/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "2"

    Scenario: Click through
        When I visit "/antibodies/"
        And I wait for the table to fully load
        When I click the link to "/antibodies/ENCAB000ACQ/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "ENCAB000ACQ"

        When I go back
        And I wait for the table to fully load
        When I click the link to "/antibodies/ENCAB000ADQ/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "ENCAB000ADQ"

#    Scenario: Detail page
#        When I visit "/antibodies/ENCAB000ANU/"
#        And I press "More"
#        Then I should see an element with the css selector "div.data-display"
#        And I should see "compliant"
#        And I should see an element with the css selector "div.characterizations"
#        And I should see at least 1 elements with the css selector "section"
#        And I should see at least 1 elements with the css selector "figure"
#        And I should see at least 1 elements with the css selector "img.characterization-img"
#        And I should see "Bradley Bernstein, Broad"
#        And I should see "U54HG006991"
