@cart @usefixtures(workbook)
Feature: Cart
    Scenario: Search result cart toggles:
        When I visit "/search/?type=Experiment"
        And I wait for the content to load
        Then I should see 25 elements with the css selector ".result-item__cart-control"

        When I press "/experiments/ENCSR123MRN/"
        And I press "/experiments/ENCSR003CON/"
        And I press "/experiments/ENCSR001CON/"
        And I press "/experiments/ENCSR000DZQ/"
        Then I should see 4 elements with the css selector ".cart__toggle--in-cart"
        And I should see an element with the css selector ".cart__nav-button"

    Scenario: Cart page load
        When I press "cart-control"
        And I click the link to "/cart-view/"
        And I wait for the content to load
        Then I should see 4 elements with the css selector ".result-item"
        And I should see "4 files selected"
        When I click the link to "#processeddata"
        Then I should see 4 elements with the css selector ".cart-list-item"
        When I click the link to "#rawdata"
        Then I should see 3 elements with the css selector ".cart-list-item"

    Scenario: Cart page interactions
        When I click the link to "#processeddata"
        And I press "output_type-label"
        And I press "cart-facet-term-alignments"
        Then I should see "2 files selected"
        And I should see 2 elements with the css selector ".cart-list-item"
        When I press "cart-facet-term-alignments"
        Then I should see "4 files selected"
        And I should see 4 elements with the css selector ".cart-list-item"
        When I press "Download processed data files"
        Then I should see an element with the css selector ".modal"
        When I press "Close"
        Then I should not see an element with the css selector ".modal"
        When I click the link to "#datasets"
        And I press "/experiments/ENCSR003CON/"
        And I wait for the content to load
        Then I should see 3 elements with the css selector ".result-item"
        And I should see "4 files selected"

    Scenario: Download menu
        When I press "cart-download"
        Then I should see 3 elements with the css selector ".menu-item"
        When I press "raw"
        Then I should see "Download raw data files"

    Scenario: Dirty cart
        When I visit "/search/?type=Experiment"
        And I dismiss the alert
        Then the browser's URL should be "/cart-view/"

    Scenario: Clearing the cart 
        When I press "clear-cart-actuator"
        Then I should see an element with the css selector ".modal"
        When I press "clear-cart-submit"
        Then I should not see an element with the css selector ".modal"
        And I should see "Empty cart"
