@search @usefixtures(workbook)
Feature: Search
    Background:
        When I visit "/search"
        And I wait for the content to load


    Scenario: Search
        Then the title should contain the text "Search"


    Scenario: Search Antibodies
        When I press "Materials & Methods"
        And I click the link to "/search/?type=AntibodyLot"
        And I wait for the content to load
        Then I should see at least 15 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 5 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=AntibodyLot&targets.organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=AntibodyLot&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal"
        And I wait for the content to load
        Then I should see at least 7 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=AntibodyLot&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal&clonality=monoclonal"
        And I wait for the content to load
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search Biosamples
        When I press "Materials & Methods"
        And I click the link to "/search/?type=Biosample"
        And I wait for the content to load
        Then I should see at least 22 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 7 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=Biosample&sex=unknown"
        And I wait for the content to load
        Then I should see at least 1 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=Biosample&sex=unknown&organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see at least 13 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search Experiments
        When I press "Data"
        And I click the link to "/search/?type=Experiment"
        And I wait for the content to load
        Then I should see at least 13 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 3 elements with the css selector "div.box.facets > div.orientation > div.facet"

        When I click the link to "?type=Experiment&assay_title=ChIP-seq"
        And I wait for the content to load
        Then I should see at least 3 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=Experiment&assay_title=ChIP-seq&assay_title=DNAme+array"
        And I wait for the content to load
        Then I should see at least 5 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search BoxI
        When I fill in "searchTerm" with "ChIP-seq"
        Then I should see at least 25 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search BoxII
        When I fill in "searchTerm" with "PMID:23000965"
        Then I should see at least 1 elements with the css selector "ul.nav.result-table > li"


    Scenario: Search BoxIII
        When I fill in "searchTerm" with "@type:Experiment date_released:[2016-01-01 TO 2016-02-01]"
        Then I should see at least 25 elements with the css selector "ul.nav.result-table > li"


