@targets @usefixtures(workbook)
Feature: Targets

    Scenario: Collection
        When I visit "/targets/"
        And I wait for the content to load
        Then I should see an element with the css selector ".view-item.type-TargetCollection"

    Scenario: Click through
        When I visit "/targets/"
        And I wait for the content to load
        When I click the link to "/search/?type=Target&organism.scientific_name=Homo+sapiens"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 21 of 21 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=Target&investigated_as=transcription+factor"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 15 of 15 results"
