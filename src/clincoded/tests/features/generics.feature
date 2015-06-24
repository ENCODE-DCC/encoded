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
        | item_type                     | link_text                             |
        | diseases                      | 183660                                |

# must log in for users
