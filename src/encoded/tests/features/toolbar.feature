@toolbar
Feature: Toolbar

    Scenario: Active section
        When I visit "/"
        #Then I should see an element with the css selector "#global-sections > li.active > a[href='/']"
        Then I should not see an element with the css selector "#global-sections > li.active > a:not([href='/'])"
        And I should see an element with the css selector "#loginbtn"
        And I should see "The Encyclopedia of DNA Elements"
