@generics @usefixtures(workbook)
Feature: Generics

    Scenario Outline: Generics
        When I visit "/<item_type>/"
        Then I should see an element with the css selector ".collection-table"
        And I wait for the table to fully load
        And I should see an element with the css selector ".collection-table > tbody > tr"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"

        When I click the link with text that contains "<link_text>"
        Then I should see an element with the css selector ".view-item.type-<item_type>"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"

        When I go back
        Then I should see an element with the css selector ".collection-table"

    Examples: Collections
        | item_type             | link_text                             |
        | antibody_approval     | ENCAB000ACQ                           |
        | antibody_lot          | ENCAB000ACQ                           |
        | antibody_validation   | 05a22a07-ab5c-42ad-bf93-801f03b017f7  |
        | award                 | A DATA COORDINATING CENTER FOR ENCODE |
        | biosample             | ENCBS000AAA                           |
        | construct             | 893d806f-3a88-43eb-afdf-dcc16c79ee45  |
        | construct_validation  | 297fab1b-3afd-4a5b-a222-ecd4c7ad1fc8  |
        | document              | 048d1185-2502-4f0e-a043-bbc75b9dd915  |
        | experiment            | ENCSR000ACY                           |
        | file                  | ENCFF000LSP                           |
        | human_donor           | ENCDO017AAA                           |
        | lab                   | Cherry                                |
        | library               | ENCLB055ZZZ                           |
        | mouse_donor           | ENCDO012AAA                           |
        | organism              | human                                 |
        | platform              | Illumina HiSeq 2000                   |
        | replicate             | 2bf12e3c-1d00-4e9f-bbc6-0cced1414f7f  |
        | rnai                  | d2dc22ba-5e7c-4626-87ac-257c6fff090c  |
        | source                | Abcam                                 |
        | target                | ADNP                                  |
        | treatment             | 2e33a097-412c-4646-87f9-858dfaaa7c06  |

# must log in for users
