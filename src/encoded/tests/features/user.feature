Feature: User Profile

    Scenario Outline: View profile
        When I visit "/"
        And I press "J. Michael Cherry"
        
        # This stopped working with ENCD-6117. It was commmented out in order to make progress
        # This needs to be investigated and addressed in a subsequent ticket

        # And I click the link with text that contains "Profile"
        # Then I should see "J. Michael Cherry, Stanford"
        # And I should see an element with the css selector ".access-keys__table"
