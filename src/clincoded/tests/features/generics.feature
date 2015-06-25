@generics @usefixtures(workbook)
Feature: Generics

    Scenario Outline: Generics
        When I visit "/<item_type>/"
        Then I should see "<link_text>"

    Examples: Collections
        | item_type                     | link_text                             |
        | diseases                      | Orphanet                                |

# must log in for users
