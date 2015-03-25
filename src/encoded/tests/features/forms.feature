@forms @usefixtures(workbook,admin_user)
Feature: Edit forms

	Scenario: Save a change to an antibody
		When I visit "/antibodies/ENCAB728YTO/"
		And I wait for the content to load
		And I click the element with the css selector ".icon-gear"
		And I click the link to "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And I fill in "antigen_description" with "It's not a very nice antigen"
		And I press "Save"
		And I wait for an element with the css selector ".view-item.type-antibody_lot" to load
		Then I should see "It's not a very nice antigen"

	Scenario: Validation errors are shown in context
		When I visit "/antibodies/ENCAB728YTO/#!edit"
		And I wait for an element with the css selector "form.rf-Form" to load
		And I fill in "date_created" with "bogus"
		And I press "Save"
		Then I should see "u'bogus' is not valid under any of the given schemas"
		And I should see an element with the css selector "input[name=date_created] + .rf-Message"
