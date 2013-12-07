@search @usefixtures(workbook)
Feature: Title

    Scenario: Search Antibodies
        When I visit "/search"
        And I wait for the content to load
        Then the title should contain the text "Search"
        When I click the link to "/search/?type=antibody_approval"
        And I wait for the content to load

	Scenario: Search Biosamples
		When I visit "/search"
		And I wait for the content to load
		Then the title should contain the text "Search"
		When I click the link to "/search/?type=biosample"
		And I wait for the content to load

	Scenario: Search Experiments
		When I visit "/search"
		And I wait for the content to load
		Then the title should contain the text "Search"
		When I click the link to "/search/?type=experiment"
		And I wait for the content to load

	Scenario: Search Targets
		When I visit "/search"
		And I wait for the content to load
		Then the title should contain the text "Search"
		When I click the link to "/search/?type=target"
		And I wait for the content to load
        