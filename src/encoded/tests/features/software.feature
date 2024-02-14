@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Materials & Methods"
        And I wait for the content to load
        And I click the link with text that contains "Software tools"
        And I wait for the content to load
        Then the title should contain the text "Software – ENCODE"

@Summary
Feature: ENCODE Software
    Background:
        When I visit "/encode-software/?type=Software&used_by=DCC"
        And I wait for the content to load

    Scenario: ENCODE Software- Portal
        Then I should see "ENCODE Software"
        Then I should see "Software implemented and developed by the DCC (Data Coordination Center) for the Portal"
        Then I should see exactly one element with the css selector ".Portal-tab.tab-button.active"
        Then I should see exactly one element with the css selector ".result-item__data"

    Scenario: ENCODE Software- Encyclopedia
        When I click the element with the css selector ".Encyclopedia-tab.tab-button" 
        Then I should see "ENCODE Software"
        Then I should see "Software tools used in integrative analysis for the development of the Encyclopedia and SCREEN"
        Then I should see exactly one element with the css selector ".Encyclopedia-tab.tab-button.active"
        Then I should see exactly one element with the css selector ".result-item__data"

    Scenario: ENCODE Software- Uniform Processing Pipelines
        When I click the element with the css selector ".Pipeline-tab.tab-button"
        Then I should see "ENCODE Software"
        Then I should see "Software implemented and developed by the DCC (Data Coordination Center) for uniforming processing of data"
        Then I should see exactly one element with the css selector ".Pipeline-tab.tab-button.active"
        Then I should see 0 elements with the css selector ".result-item__data"

    Scenario: ENCODE Software- Consortium Analysis
        When I click the element with the css selector ".AWG-tab.tab-button"
        Then I should see "ENCODE Software"
        Then I should see "Software tools implemented and developed by the consortium for computational analysis"
        Then I should see exactly one element with the css selector ".AWG-tab.tab-button.active"
        Then I should see exactly one element with the css selector ".result-item__data"
    
    Scenario: ENCODE Software- All
        When I click the element with the css selector ".All-tab.tab-button"
        Then I should see "ENCODE Software"
        Then I should see "All software used or developed by the ENCODE Consortium"
        Then I should see exactly one element with the css selector ".All-tab.tab-button.active"
        Then I should see 25 elements with the css selector ".result-item__data"
