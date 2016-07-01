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
        | Award                         | A DATA COORDINATING CENTER FOR ENCODE |
        | Snowflake                     | SNOFL000LSP                           |
        | Snowball                      | SNOSS704RSS                           |
        | Snowfort                      | SNOSS000AER                           |
        | Lab                           | Cherry                                |

# must log in for users
