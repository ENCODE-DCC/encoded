@forms @usefixtures(workbook,admin_user)
Feature: Edit forms

	Scenario: Save a change to an antibody
		When I visit "/antibodies/ENCAB728YTO/"
		And I wait for the content to load
		And I click the element with the css selector ".icon-gear"
		And I click the link to "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And "schema_version" should be disabled
		And I fill in "antigen_description" with "It's not a very nice antigen"
		And I press "Save"
		And I wait for an element with the css selector ".view-item.type-antibody_lot" to load
		Then I should see "It's not a very nice antigen"

	Scenario: Edit a child object
		When I visit "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And I click the element with the css selector ".collapsible-trigger"
		And I fill in "caption" with "This is the new caption"
		And I press "Save"
		And I wait for an element with the css selector ".view-item.type-antibody_lot" to load
		Then I should see "This is the new caption"

	Scenario: Leaving a dirty form without saving asks for confirmation
		When I visit "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And I fill in "antigen_description" with "It's not a very nice antigen"
		And I click the link with text "ENCODE"
		And I dismiss the alert
		Then field "antigen_description" should have the value "It's not a very nice antigen"
		# Make sure we don't leave a dirty form that will interfere with subsequent tests
		And I click the link with text "ENCODE"
		And I accept the alert

	Scenario: Validation errors are shown in context
		When I visit "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And I fill in "date_created" with "bogus"
		And I press "Save"
		And I wait for an element with the css selector "input[name=date_created] + .rf-Message" to load
		Then I should see "u'bogus' is not valid under any of the given schemas"

	# Make sure we don't leave a dirty form that can't be exited easily
	Scenario: Clean up after using forms
		When I visit "/antibodies/ENCAB728YTO/#!edit"
		And I click the link with text "ENCODE"
		And I accept the alert

# To add:
# - interacting with the object picker
# - clicking links in the form opens in new window
