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
        And I should see at least 100 elements with the css selector "table.sticky-area > tbody > tr"
        And I should see an element with the css selector "a[href='/antibodies/d6947988-8fea-4c13-b2ec-2381e7f7a84f']"
        When I fill in "table-filter" with "mouse"
        Then I should see an element with the css selector "tr:not(.hidden) a[href='/antibodies/b199b76a-6c4c-468c-a41f-bc4755618632']" within 1 seconds
        And I should see an element with the css selector "tr.hidden a[href='/antibodies/2c13cc62-987b-4fdf-b726-0535c5e4c78e']"
        And I should see exactly one element with the css selector "#table-count" containing the text "65"
        When I click the link to "/antibodies/b199b76a-6c4c-468c-a41f-bc4755618632"
        Then I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "div.data-display"
        When I visit "/antibodies/643fd427-99d2-4759-a18d-85c0c89da0ab"
        Then I should see an element with the css selector "#content.container"
        And I should see an element with the css selector "div.data-display"
        And I should see an element with the css selector "div.validations"
        And I should see at least 2 elements with the css selector "section"
        And I should see at least 2 elements with the css selector "figure"
        And I should see at least 2 elements with the css selector "img.validation-img"
