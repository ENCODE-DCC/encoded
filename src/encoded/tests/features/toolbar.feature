@toolbar
Feature: Toolbar

    Scenario: Active section
        When I visit "/"
        #Then I should see an element with the css selector "#global-sections > li.active > a[href='/']"
        Then I should not see an element with the css selector "#global-sections > li.active > a:not([href='/'])"
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/antibodies/']"
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/biosamples/']"
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/targets/']"
        And I should see an element with the css selector "#global-sections > li:not(.active) > a[href='/experiments/']"
        And I should see an element with the css selector "#user-actions > li > [data-trigger='login']"
        And I should not see an element with the css selector "#user-actions > li[style='display: none;'] > [data-trigger='logout']"
        And I should see "The Encyclopedia of DNA Elements"
