@antibodies @usefixtures(workbook)
Feature: Antibodies

    Scenario: Active section
        When I visit "/antibodies/"
        Then the "/antibodies/" section should be active

    Scenario: Table
        When I visit "/antibodies/"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 15 elements with the css selector "table.sticky-area > tbody > tr"
        When I wait for the table to fully load
        Then I should see an element with the css selector "a[href='/antibodies/c808814f-376f-41ee-b93e-ddd00294ca3d/']"

        When I fill in "q" with "mouse"
        Then I should see an element with the css selector "tr:not([hidden]) a[href='/antibodies/97d18178-73f7-47c2-a9f0-3ff1c4f0fed5/']" within 1 seconds
        And I should see an element with the css selector "tr[hidden] a[href='/antibodies/c808814f-376f-41ee-b93e-ddd00294ca3d/']"
        And I should see exactly one element with the css selector ".table-count" containing the text "8"

    Scenario: Click through
        When I visit "/antibodies/"
        And I wait for the table to fully load
        When I click the link to "/antibodies/f2942c07-0f9b-4e05-b9df-1c5afbd45446/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "INCOMPLETE"
        And I should see "mouse CTCF"

        When I go back
        And I wait for the table to fully load
        When I click the link to "/antibodies/68374220-d4de-4114-bc78-4b1c21f03711/"
        And I should see an element with the css selector "div.data-display"
        And I should see "SUBMITTED"
        And I should see "CTCF"

        #When I go back
        #And I wait for the table to fully load
        #When I click the link to "/antibodies/f2942c07-0f9b-4e05-b9df-1c5afbd45446/"
        #Then I should see an element with the css selector "div.data-display"
        #And I should see "INCOMPLETE"

    Scenario: Detail page
        When I visit "/antibodies/97d18178-73f7-47c2-a9f0-3ff1c4f0fed5/"
        Then I should see an element with the css selector "div.data-display"
        And I should see "INCOMPLETE"
        And I should see an element with the css selector "div.validations"
        And I should see at least 1 elements with the css selector "section"
        And I should see at least 1 elements with the css selector "figure"
        And I should see at least 1 elements with the css selector "img.validation-img"
        And I should see "Bradley Bernstein, Broad"
        And I should see "U54HG004570"
        And I should see "Ross Hardison, PennState"
        And I should see "RC2HG005573"

    Scenario: Detail page 2
        When I visit "/antibodies/67f66ceb-5e06-4f9d-95f0-06c51897199f/"
        And I should see an element with the css selector "div.data-display"
        And I should see "APPROVED"

