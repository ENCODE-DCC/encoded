@antibodies @usefixtures(index_workbook)
Feature: Antibodies

    Scenario: Collection
        When I visit "/antibodies/"
        And I wait for the content to load
        Then I should see an element with the css selector ".view-item.type-AntibodyLotCollection"

    Scenario: Click through
        When I visit "/antibodies/"
        And I wait for the content to load
        When I click the link to "/search/?type=AntibodyLot&targets.organism.scientific_name=Homo+sapiens"
        Then I should see an element with the css selector "div.search-results"
        And I should see "Showing 13 of 13 results"

        When I go back
        And I wait for the content to load
        When I click the link to "/search/?type=AntibodyLot&lot_reviews.status=characterized+to+standards"
        Then I should see an element with the css selector "div.search-results"
        And I should see "Showing 4 of 4 results"
