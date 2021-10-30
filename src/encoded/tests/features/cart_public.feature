@cart
Feature: Cart
    Scenario: View cart listing
        When I visit "/"
        And I wait for the content to load
        And I press "cart-control"
        And I click the link with text that contains "Listed carts"
        And I wait for the content to load
        Then I should see 1 elements with the css selector ".result-item__wrapper"

        When I press "More"
        And I wait for 1 seconds
        Then I should see "billions upon billions"

        When I press "Less"
        And I wait for 1 seconds
        Then I should not see "billions upon billions"
