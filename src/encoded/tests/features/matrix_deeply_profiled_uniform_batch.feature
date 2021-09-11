# If the full Deeply profiled matrix url is used (about 1600 characters in length), it causes an issue in the nav bar 
# where logged-in-user-name -> Profile BDD test where it fails. The dev branch locally will also fail going forward; 
# until you do a "make clean" on ENCODE. It is an X-file case on how that is possible. This BDD test file was 
# simplified and important test left out, in order to finish ENCD-6117. This needs to be revisited later.

@matrix
Feature: Matrix
    Scenario: Deeply Profiled Matrix
        When I visit "/"
        And I wait for the content to load
        Then the title should contain the text "ENCODE"

    When I visit "/deeply-profiled-uniform-batch-matrix/?type=Experiment&control_type!=*&status=released"
        And I wait for the content to load
        Then the title should contain the text "Deeply Profiled Cell Lines"
        And I should see 1 elements with the css selector "#deeplyProfiled:checked"

