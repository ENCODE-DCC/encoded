Feature: Toolbar

    Background:
        Given a browser    

    Scenario: Active section
        When I visit "/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/'])"
        When I visit "/antibodies/"
        Then I should see an element with the css selector "#global-sections > li.active > a[href='/antibodies/']"
        And I should not see an element with the css selector "#global-sections > li.active > a:not([href='/antibodies/'])"
