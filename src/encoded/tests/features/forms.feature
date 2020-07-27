@forms @usefixtures(index_workbook,admin_user)
Feature: Edit forms

    Scenario: Save a change to an antibody
        When I visit "/antibodies/ENCAB728YTO/"
        And I wait for the content to load
        And I click the element with the css selector ".icon-gear"
        And I click the link to "/antibodies/ENCAB728YTO/#!edit"
        And I wait for the content to load
        And I wait for 20 seconds
        And I wait for an element with the css selector "form.rf-Form" to load
        Then I should see an element with the css selector "form.rf-Form"
        When I fill in "antigen_description" with "It's not a very nice antigen"
        And I press "save"
        And I wait for 30 seconds
        And I wait for the content to load
        Then I should see "It's not a very nice antigen"

    Scenario: Leaving a dirty form without saving asks for confirmation
        When I visit "/antibodies/ENCAB728YTO/#!edit"
        And I wait for 20 seconds
        And I wait for an element with the css selector "form.rf-Form" to load
        And I fill in "antigen_description" with "It's not a very nice antigen"
        And I press "ENCODE"
        And I dismiss the alert
        Then field "antigen_description" should have the value "It's not a very nice antigen"
        # Make sure we don't leave a dirty form that will interfere with subsequent tests
        When I press "ENCODE"
        And I accept the alert
        And I wait for 20 seconds

    Scenario: Validation errors are shown in context
        When I visit "/antibodies/ENCAB728YTO/#!edit"
        And I wait for an element with the css selector "form.rf-Form" to load
        And I fill in "date_created" with "bogus"
        And I wait for an element with the css selector ".rf-Message + input[name=date_created]" to load
        Then I should see "is not any of" within 5 seconds
        # Make sure we don't leave a dirty form that will interfere with subsequent tests
        When I press "ENCODE"
        And I accept the alert

# To add:
# - interacting with the object picker
# - clicking links in the form opens in new window
