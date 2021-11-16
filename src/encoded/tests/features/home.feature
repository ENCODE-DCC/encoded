@home
Feature: Home page

    Scenario: Elements
        When I visit "/"
        And I wait for the content to load
        Then I should see an element with the css selector ".home-search-section"
        And I should see at least 4 elements with the css selector ".home-section"

    Scenario: Click cards
        When I click the link with text that contains "Functional characterization"
        And I wait for the content to load
        Then I should not see an element with the css selector ".home-search-section"
        And I should see at least 1 elements with the css selector ".result-item--type-FunctionalCharacterizationSeries"
        And I should see at least 1 elements with the css selector ".result-item--type-FunctionalCharacterizationExperiment"

        When I go back
        And I wait for the content to load
        And I click the link with text that contains "Region search"
        And I wait for the content to load
        Then I should not see an element with the css selector ".home-search-section"
        And I should see an element with the css selector ".adv-search-form"

    Scenario: Click help
        When I go back
        And I wait for the content to load
        And I press "card-help-rush-ad"
        Then I should see an element with the css selector ".modal"

        When I press "close-modal"
        Then I should not see an element with the css selector ".modal"

    Scenario: Collection search
        When I fill in "search-input-native" with "human"
        And I wait for 3 seconds
        Then I should see 7 elements with the css selector ".card--highlighted"
        And I should see 3 elements with the css selector ".card-count"
        And I should see an element with the css selector ".home-search-section__supplement.home-search-section__supplement--native"
        And I should see at least 8 elements with the css selector ".native-top-hit"

        When I click the link with text that contains "Encyclopedia of elements"
        And I wait for the content to load
        Then I should see an element with the css selector ".clear-search-term__control"

        When I go back
        And I wait for the content to load
        And I wait for 3 seconds
        Then field "search-input-native" should have the value "human"
        Then I should see 7 elements with the css selector ".card--highlighted"
        And I should see 3 elements with the css selector ".card-count"
        And I should see an element with the css selector ".home-search-section__supplement.home-search-section__supplement--native"
        And I should see at least 8 elements with the css selector ".native-top-hit"

    Scenario: SCREEN search
        When I press "search-mode-select-screen"
        And I wait for 1 seconds
        Then I should see "Search SCREEN"
        And I should see an element with the css selector ".home-search-section__supplement.home-search-section__supplement--screen"

        # Including a test of SCREEN inputs makes sense here, but I decided not to include any
        # because failures in screen.wenglab.org will cause our BDD tests to fail.