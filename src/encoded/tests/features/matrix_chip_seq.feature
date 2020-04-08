@matrix @usefixtures(workbook)
Feature: Matrix
    Scenario: ChIP-seq matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

        When I press "Data"
        And I click the link with text that contains "ChIP-seq matrix"
        And I wait for the content to load
        Then the title should contain the text "ChIP-seq Matrix – ENCODE"
        And I should see at least 5 elements with the css selector "tbody > tr"
        And I should see at least 3 elements with the css selector "tr > th"

        When I click the link with text that contains "Mus musculus"
        Then I should see at least 2 elements with the css selector "tbody > tr"
        And I should see at least 2 elements with the css selector "tr > th"

    Scenario: Organism chooser modal
        When I visit "/chip-seq-matrix/?type=Experiment"
        And I wait for the content to load
        Then I should see exactly one element with the css selector ".modal"
        And I should see at least 2 elements with the css selector ".chip_seq_matrix__organism-selector > .selectors > .btn"

        When I click the element with the css selector ".btn__selector--Homo-sapiens"
        And I wait for the content to load
        Then I should not see an element with the css selector ".modal"
        And I should see at least 5 elements with the css selector "tbody > tr"
        And I should see at least 7 elements with the css selector "tr > th"
