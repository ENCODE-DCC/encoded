@forms @usefixtures(workbook,admin_user)
Feature: Edit forms

    Scenario: Save a change to an snowflake
        When I visit "/snowflakes/SNOFL000LSP/"
        And I wait for the content to load
        And I click the element with the css selector ".icon-gear"
        And I click the link to "/snowflakes/SNOFL000LSP/#!edit"
        And I wait for an element with the css selector "form.rf-Form" to load
        And I select "slushy" from "type"
        And I press "Save"
        And I wait for an element with the css selector ".view-item.type-Snowflake" to load
        Then I should see "slushy"

    Scenario: Leaving a dirty form without saving asks for confirmation
        When I visit "/snowflakes/SNOFL001MXE/#!edit"
        And I wait for an element with the css selector "form.rf-Form" to load
        And I select "slushy" from "type"
        And I click the link with text "SNOWFLAKES"
        And I dismiss the alert
        Then field "type" should have the value "slushy"
        # Make sure we don't leave a dirty form that will interfere with subsequent tests
        When I click the link with text "SNOWFLAKES"
        And I accept the alert

    Scenario: Validation errors are shown in context
        When I visit "/snowflakes/SNOFL001MYM/#!edit"
        And I wait for an element with the css selector "form.rf-Form" to load
        And I fill in "date_created" with "bogus"
        And I press "Save"
        And I wait for an element with the css selector "input[name=date_created] + .rf-Message" to load
        Then I should see "'bogus' is not valid under any of the given schemas" within 2 seconds
        # Make sure we don't leave a dirty form that will interfere with subsequent tests
        When I click the link with text "SNOWFLAKES"
        And I accept the alert

# To add:
# - interacting with the object picker
# - clicking links in the form opens in new window
