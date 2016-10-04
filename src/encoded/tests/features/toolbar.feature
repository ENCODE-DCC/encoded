@toolbar
Feature: Toolbar

    Scenario: Active section
        When I visit "/"
        #Then I should see an element with the css selector "#global-sections > li.active > a[href='/']"
        Then I should not see an element with the css selector "#global-sections > li.active > a:not([href='/'])"
        And I should see an element with the css selector "#user-actions-footer > [data-trigger='login']"
        And I should see "Encyclopedia of DNA Elements"
