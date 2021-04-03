@search
Feature: Search
    Background:
        When I visit "/searchv2_raw/?type=Experiment"
        And I wait for the content to load


    Scenario: Search
        Then I should see 1 elements with the css selector ".view-detail.panel pre"
        And I should not see "Server Rendering Error"
