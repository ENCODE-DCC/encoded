@antibodies @usefixtures(workbook)
Feature: Antibodies

    Scenario: Collection
        When I visit "/antibodies/"
        And I wait for the content to load
        Then I should see an element with the css selector ".view-item.type-AntibodyLotCollection"

    Scenario: Click through
        When I visit "/antibodies/"
        And I wait for the content to load
        When I click the link to "/search/?type=AntibodyLot&targets.organism.scientific_name=Homo+sapiens"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 14 of 14 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=AntibodyLot&lot_reviews.status=characterized+to+standards"
        Then I should see an element with the css selector "div.panel.data-display.main-panel"
        And I should see "Showing 3 of 3 results"
