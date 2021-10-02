@Summary
Feature: Encyclopedia
    Scenario: Encyclopedia
        When I visit "/encyclopedia/?type=File&annotation_type=candidate+Cis-Regulatory+Elements&assembly=GRCh38&file_format=bigBed&file_format=bigWig"
        And I wait for the content to load
        Then I should see "Encyclopedia - Integrative Annotations"

        When I press "Mus musculus"
        And I wait for the content to load
        Then I should see "There are 0 files displayed out of 0 files that match the selected filters."

        When I press "Homo sapiens"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".file-gallery-facet-redirect"
