@biosamples @usefixtures(workbook)
Feature: Biosamples

    Scenario: Detail page
        When I visit "/biosamples/ENCBS000AAA/"
        Then I should see "Richard Myers, HAIB"
        And I should see "ENCODE"

    Scenario: Collection
        When I visit "/biosamples/"
        And I wait for the content to load
        Then I should see an element with the css selector ".view-item.type-BiosampleCollection"

    Scenario: Click through
        When I visit "/biosamples/"
        And I wait for the content to load
        When I click the link to "/search/?type=Biosample&organism.scientific_name=Homo+sapiens"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 25 of 30 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=Biosample&status=in+progress"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 25 of 36 results"
