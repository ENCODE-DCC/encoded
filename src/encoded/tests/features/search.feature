@search @usefixtures(workbook)
Feature: Search
    Background:
        When I visit "/search"
        And I wait for the content to load


    Scenario: Search
        Then the title should contain the text "Search"


    Scenario: Search Antibodies
        When I visit "/search/?type=AntibodyLot&status=released"
        And I wait for the content to load
        Then I should see at least 7 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 5 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see at least 6 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal&clonality=monoclonal"
        And I wait for the content to load
        Then I should see at least 6 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search Biosamples
        When I visit "/search/?type=Biosample&status=released"
        And I wait for the content to load
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 7 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=Biosample&status=released&sex=unknown"
        And I wait for the content to load
        Then I should see at least 7 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=Biosample&status=released&sex=unknown&organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search Experiments
        When I press "Data"
        And I click the link to "/search/?type=Experiment&internal_tags=RegulomeDB"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 3 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=Experiment&internal_tags=RegulomeDB&assay_title=ChIP-seq"
        And I wait for the content to load
        Then I should see at least 2 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=Experiment&internal_tags=RegulomeDB&assay_title=ChIP-seq&assay_title=DNase-seq"
        And I wait for the content to load
        Then I should see at least 3 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search TermI
        When I visit "/search/?searchTerm=ChIP-seq"
        Then I should see at least 25 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search TermII
        When I visit "/search/?searchTerm=PMID:23000965"
        Then I should see at least 1 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search TermIII
        When I visit "/search/?searchTerm=@type:Experiment date_released:[2016-01-01 TO 2016-02-01]"
        Then I should see at least 25 elements with the css selector "ul.nav.result-table > li"
