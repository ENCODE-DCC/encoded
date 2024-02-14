@matrix
Feature: Matrix
    Scenario: Humsn Donor Matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Human donor matrix"
        And I wait for the content to load
        Then the title should contain the text "Human Donor Matrix – ENCODE"
        And I should see exactly one element with css selector "body-map-thumbnail-and-modal"
        And I should see at exactly 8 elements with the css selector ".grid-matrix > *"
        And I should see at exactly 8 elements with the css selector ".human-donor-biosample__body__options div"
        And I should see at exactly 1 elements with the css selector  ".human-donor-biosample__body__options div :checked[id=\"tissue-option\"]"
        And I should see at least 8 elements with the css selector ".human-donor-legend--disease-text"
