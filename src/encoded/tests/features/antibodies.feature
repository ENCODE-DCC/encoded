Feature: Antibodies

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/antibodies/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/antibodies/']" within 5 seconds
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/sources/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/antibodies/'])"
        And I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 15 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/antibodies/c808814f-376f-41ee-b93e-ddd00294ca3d']"

        When I click the link to "/antibodies/f2942c07-0f9b-4e05-b9df-1c5afbd45446"
        Then I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "div.data-display"
        And I should see "INCOMPLETE"
        And I should see "mouse CTCF"

        When I go back
        When I click the link to "/antibodies/68374220-d4de-4114-bc78-4b1c21f03711"
        Then I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "div.data-display"
        And I should see "SUBMITTED"
        And I should see "CTCF"

        When I go back
        When I fill in "table-filter" with "mouse"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/antibodies/97d18178-73f7-47c2-a9f0-3ff1c4f0fed5']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/antibodies/c808814f-376f-41ee-b93e-ddd00294ca3d']"
        And I should see exactly one element with the css selector "#table-count" containing the text "8"

        #When I click the link to "/antibodies/f2942c07-0f9b-4e05-b9df-1c5afbd45446"
        #Then I should see an element with the css selector "#content.container"
        #And I should see an element with the css selector "div.data-display"
        #And I should see "INCOMPLETE"
        When I visit "/antibodies/97d18178-73f7-47c2-a9f0-3ff1c4f0fed5"
        Then I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "div.data-display"
        And I should see "APPROVED"
        And I should see an element with the css selector "div.validations"
        And I should see at least 1 elements with the css selector "section"
        And I should see at least 1 elements with the css selector "figure"
        And I should see at least 1 elements with the css selector "img.validation-img"
        And I should see ". Bernstein / Bradley Bernstein, Broad / ENCODE2"
