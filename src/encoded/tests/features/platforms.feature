@platforms @usefixtures(workbook)
Feature: Platforms

    Background:
        Given a browser

    Scenario: Active section
        When I visit "/platforms/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/platforms/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not([class='active']) > a[href='/targets/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/platforms/'])"
        And I should see an element with the css selector "#content[class='container']"
        And I should see an element with the css selector "table.sticky-area"
        And I should see an element with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 5 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see at least 5 elements with the css selector "tr > td > a"
        And I should see exactly one element with the css selector "#table-count" containing the text "11"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"