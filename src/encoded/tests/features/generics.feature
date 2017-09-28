@generics @usefixtures(workbook)
Feature: Generics

    Scenario Outline: Generics
        When I visit "/<type_name>/"
        Then I should see an element with the css selector ".collection-table"
        When I wait for the table to fully load
        Then I should see an element with the css selector ".collection-table > tbody > tr"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"

        When I click the link with text that contains "<link_text>"
        Then I should see an element with the css selector ".view-item.type-<type_name>"
        And I should not see "N/A"
        And I should not see "NULL"
        And I should not see "null"

        When I go back
        Then I should see an element with the css selector ".collection-table"

    Examples: Collections
        | type_name                     | link_text                             |
        | AntibodyLot                   | ENCAB000ACQ                           |
        | AntibodyCharacterization      | 05a22a07-ab5c-42ad-bf93-801f03b017f7  |
        | Award                         | A DATA COORDINATING CENTER FOR ENCODE |
        | Biosample                     | ENCBS000AAA                           |
        | BiosampleCharacterization     | 297fab1b-3afd-4a5b-a222-ecd4c7ad1fc8  |
        | Construct                     | 893d806f-3a88-43eb-afdf-dcc16c79ee45  |
        | Document                      | 048d1185-2502-4f0e-a043-bbc75b9dd915  |
        | Experiment                    | ENCSR000ACY                           |
        | File                          | ENCFF000LSP                           |
        | HumanDonor                    | ENCDO017AAA                           |
        | Lab                           | Cherry                                |
        | Library                       | ENCLB055ZZZ                           |
        | MouseDonor                    | ENCDO012AAA                           |
        | Organism                      | human                                 |
        | Platform                      | Illumina HiSeq 2000                   |
        | Publication                   | integrated encyclopedia               |
        | Replicate                     | 2bf12e3c-1d00-4e9f-bbc6-0cced1414f7f  |
        | Source                        | Abcam                                 |
        | Target                        | ADNP                                  |
        | Treatment                     | 2e33a097-412c-4646-87f9-858dfaaa7c06  |

# must log in for users
