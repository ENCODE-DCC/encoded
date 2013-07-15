@jasmine
Feature: Jasmine tests

    Scenario: Jasmine tests have no failures
        When I visit "/tests/js/test_runner.html"
        Then I should see an element with the css selector ".duration"
        And I should see 0 elements with the css selector ".specDetail.failed"
