@generics @usefixtures(workbook)
Feature: Generics

    Scenario Outline: Generics
        When I visit "/<type_name>/"
        And I wait for the content to load
        Then I should see an element with the css selector ".collection-charts"
        And I should see an element with the css selector ".collection-charts > .collection-charts__chart > .collection-charts__legend"
        And I should not see "No facets defined"

        When I click the link with text that contains "<link_text>"
        Then I should see an element with the css selector ".result-table"
        And I should not see "No results found"

        When I go back
        Then I should see an element with the css selector ".collection-charts"

    Examples: Collections
        | type_name                     | link_text                             |
        | Annotation                    | other                                 |
        | AntibodyLot                   | characterized to standards            |
        | AntibodyCharacterization      | compliant                             |
        | Award                         | Bradley Bernstein, Broad              |
        | Biosample                     | Homo sapiens                          |
        | Document                      | ENCODE2 Project, UCSC                 |
        | Experiment                    | DNA binding                           |
        | File                          | released                              |
        | Library                       | released                              |
        | Publication                   | published                             |
        | Software                      | aligner                               |
        | Target                        | Homo sapiens                          |

# must log in for users
