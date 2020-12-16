@matrix @usefixtures(index_workbook)
Feature: Matrix
    Scenario: Matrix Reference Epigenome
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "Human reference epigenomes"
        And I wait for the content to load
        Then the title should contain the text "Reference Epigenome Matrix – ENCODE"
        And I should see at least 5 elements with the css selector "tbody > tr"
        And I should see at least 15 elements with the css selector "tr > th"
        And I should see exactly one element with the css selector ".test-project-selector [for='nonroadmap']"
        And I should see exactly one element with the css selector ".test-project-selector input[value='Nonroadmap']"
        And I should see exactly one element with the css selector ".test-project-selector input[value='All'][checked]"


    Scenario: Selecting an award
        When I visit "/reference-epigenome-matrix/?type=Experiment&related_series.@type=ReferenceEpigenome&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".test-project-selector input[value='Nonroadmap']"

        When I click the element with the css selector ".test-project-selector [for='nonroadmap']"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".test-project-selector input[value='Nonroadmap'][checked]"
        Then I should see exactly one element with the css selector ".nav-tabs li.active a[href='#Homo sapiens']"
        Then I should see at least 5 elements with the css selector "tbody > tr"
        And I should see at least 15 elements with the css selector "tr > th"

        When I click the link with text that contains "Mus musculus"
        Then I should see at least 4 elements with the css selector "tbody > tr"
        And I should see at least 4 elements with the css selector "tr > th"
