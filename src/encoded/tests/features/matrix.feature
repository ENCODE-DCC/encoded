@title
Feature: Title

    Scenario: Title updates
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"
        When I press "Data"
        And I click the link to "/matrix/?type=Experiment"
        And I wait for the content to load
        Then the title should contain the text "Matrix – ENCODE"

@matrix @usefixtures(workbook)
Feature: Matrix
    Background:
        When I visit "/matrix/?type=Experiment"
        And I wait for the content to load


    Scenario: Matrix
        Then the title should contain the text "Matrix"
        Then I should see at least 15 elements with the css selector "tbody > tr"
        Then I should see at least 10 elements with the css selector "tr > th"
        Then I should see at least 5 elements with the css selector "div.orientation > div.facet"


    Scenario: Matrix Encyclopedia
        When I press "Encyclopedia"
        And I click the link to "/matrix/?type=Annotation&encyclopedia_version=4"
        And I wait for the content to load
        Then I should see at least 1 elements with the css selector "div.matrix-wrapper > div.matrix-group-heading > div.matrix-group-heading__content"
        And I should see at least 1 elements with the css selector "div.matrix-wrapper > table.matrix"