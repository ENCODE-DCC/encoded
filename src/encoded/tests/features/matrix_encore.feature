@matrix @usefixtures(index_workbook)
Feature: Matrix
    Scenario: Matrix ENCORE
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        # Main ENCORE matrix
        When I press "Data"
        And I click the link with text that contains "RNA-protein interactions (ENCORE)"
        And I wait for the content to load
        Then the title should contain the text "ENCORE Matrix – ENCODE"
        And I should see at least 4 elements with the css selector ".matrix.matrix--encore tbody > tr"
        And I should see 1 elements with the css selector ".matrix.matrix--encore tr.matrix__col-category-header > th"
        And I should see 2 elements with the css selector ".matrix.matrix--encore tr.matrix__col-category-subheader > th"
        And I should see 2 elements with the css selector ".matrix.matrix--encore tr.matrix__row-data"
        # Inset RNA-seq matrix
        And I should see 1 elements with the css selector ".matrix__rna-seq"
        And I should see 1 elements with the css selector ".matrix.matrix--rna-seq"
        And I should see at least 3 elements with the css selector ".matrix.matrix--rna-seq > tbody > tr"
        And I should see 1 elements with the css selector ".matrix.matrix--rna-seq tr.matrix__col-category-header > th"
        And I should see 1 elements with the css selector ".matrix.matrix--rna-seq tr.matrix__col-category-subheader > th"
        And I should see 1 elements with the css selector ".matrix.matrix--rna-seq tr.matrix__row-data > th"

    Scenario: Matrix ENCORE filtering
        When I fill in "target-filter" with "TAF"
        Then I should see 1 elements with the css selector ".matrix.matrix--encore tr.matrix__row-data"
