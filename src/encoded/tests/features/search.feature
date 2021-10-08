@search
Feature: Search
    Background:
        When I visit "/search"
        And I wait for the content to load


    Scenario: Search
        Then the title should contain the text "Search"


    Scenario: Search Antibodies
        When I press "Materials & Methods"
        And I wait for the content to load
        And I click the link to "/search/?type=AntibodyLot&status=released"
        And I wait for the content to load
        Then I should see at least 7 elements with the css selector "ul.result-table > li"
        And I should see at least 5 elements with the css selector "div.box.facets > div.orientation > div.facet-list-wrapper > div.facet"

        When I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see at least 6 elements with the css selector "ul.result-table > li"

        When I press "facet-expander-clonality"
        And I wait for 1 seconds
        And I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "ul.result-table > li"

        When I click the link to "?type=AntibodyLot&status=released&targets.organism.scientific_name=Homo+sapiens&clonality=polyclonal&clonality=monoclonal"
        And I wait for the content to load
        Then I should see at least 6 elements with the css selector "ul.result-table > li"



    Scenario: Search Experiments
        When I press "Data"
        And I click the link to "/search/?type=Experiment&control_type!=*&status=released&perturbed=false"
        And I wait for the content to load
        Then I should see at least 25 elements with the css selector "ul.result-table > li"
        And I should see at least 3 elements with the css selector "div.box.facets > div.orientation > div.facet-list-wrapper > div.facet-group"

        When I click the link to "?type=Experiment&control_type!=*&status=released&perturbed=false&assay_title=TF+ChIP-seq"
        And I wait for the content to load
        Then I should see at least 2 elements with the css selector "ul.result-table > li"

        When I click the link to "?type=Experiment&control_type!=*&status=released&perturbed=false&assay_title=TF+ChIP-seq&assay_title=DNAme+array"
        And I wait for the content to load
        Then I should see at least 4 elements with the css selector "ul.result-table > li"


    Scenario: Search BoxI
        When I fill in "searchTerm" with "ChIP-seq"
        Then I should see at least 25 elements with the css selector "ul.result-table > li"


    Scenario: Search BoxII
        When I fill in "searchTerm" with "PMID:23000965"
        Then I should see at least 1 elements with the css selector "ul.result-table > li"


    Scenario: Search BoxIII
        When I fill in "searchTerm" with "@type:Experiment date_released:[2016-01-01 TO 2016-02-01]"
        Then I should see at least 25 elements with the css selector "ul.result-table > li"

   Scenario: Search for Assay term
        When I press "Data"
        And I click the link to "/search/?type=Experiment&control_type!=*&status=released&perturbed=false"
        And I wait for the content to load
        And I fill in "searchAssaytitle" with "dna"
        Then I should see at least 2 elements with the css selector "div.facet__term-list.searchAssaytitle > li"

    Scenario: Search for Target of Assay term
        When I press "Data"
        And I click the link to "/search/?type=Experiment&control_type!=*&status=released&perturbed=false"
        And I wait for the content to load
        And I fill in "searchTargetofassay" with "fkh-10"
        Then I should see at least 1 elements with the css selector "div.facet__term-list.searchTargetofassay > li"

    Scenario: Search for Organ term
        When I press "Data"
        And I click the link to "/search/?type=Experiment&control_type!=*&status=released&perturbed=false"
        And I wait for the content to load
        And I press "facet-group-Biosample-Experiment-title"
        And I press "facet-expander-biosample_ontology.organ_slims"
        And I wait for 1 seconds
        And I fill in "searchOrgan" with "zzz"
        Then I should see 0 elements with the css selector "div.facet__term-list.searchOrgan > li"

    Scenario: Smoke testing advanced query search
        When I fill in "searchTerm" with "@type:Experiment  date_created:[2015-01-01 TO 2018-12-31]"
        Then I should see at least 25 elements with the css selector "ul.result-table > li"
