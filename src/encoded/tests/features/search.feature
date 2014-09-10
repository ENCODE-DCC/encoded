@search @usefixtures(workbook)
Feature: Search

    Scenario: Search
        When I visit "/search"
        And I wait for the content to load
        Then the title should contain the text "Search"

    
    Scenario: Search Antibodies
        When I click the link with text that contains "Data"
        And I click the link to "/search/?type=antibody_lot"
        And I wait for the content to load
        And I should see at least 15 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 5 elements with the css selector "div.box.facets > div.facet"
        
        When I click the link to "?type=antibody_lot&characterizations.target.organism.scientific_name=Homo sapiens"
        And I wait for the content to load
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"
        
        When I click the link to "?type=antibody_lot&characterizations.target.organism.scientific_name=Homo%20sapiens&clonality=polyclonal"
        And I wait for the content to load
        Then I should see at least 7 elements with the css selector "ul.nav.result-table > li"
        
        When I click the link to "?type=antibody_lot&characterizations.target.organism.scientific_name=Homo%20sapiens&clonality=polyclonal&clonality=monoclonal"
        And I wait for the content to load
        Then I should see at least 10 elements with the css selector "ul.nav.result-table > li"
        

    Scenario: Search Biosamples
        When I click the link with text that contains "Data"
        And I click the link to "/search/?type=biosample"
        And I wait for the content to load
        And I should see at least 22 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 7 elements with the css selector "div.box.facets > div.facet"
        
        When I click the link to "?type=biosample&sex=unknown"
        And I wait for the content to load
        Then I should see at least 1 elements with the css selector "ul.nav.result-table > li"
        
        When I click the link to "?type=biosample&sex=unknown&organism.scientific_name=Homo sapiens"
        And I wait for the content to load
        Then I should see at least 13 elements with the css selector "ul.nav.result-table > li"
        

    Scenario: Search Experiments
        When I click the link with text that contains "Data"
        And I click the link to "/search/?type=experiment"
        And I wait for the content to load
        And I should see at least 13 elements with the css selector "ul.nav.result-table > li"
        And I should see at least 3 elements with the css selector "div.box.facets > div.facet"
        
        When I click the link to "?type=experiment&assay_term_name=ChIP-seq"
        And I wait for the content to load
        Then I should see at least 3 elements with the css selector "ul.nav.result-table > li"

        When I click the link to "?type=experiment&assay_term_name=ChIP-seq&assay_term_name=MethylArray"
        And I wait for the content to load
        Then I should see at least 5 elements with the css selector "ul.nav.result-table > li"
