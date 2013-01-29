Feature: Antibody approval
    In order to approve antibody validation images
    As an approver I need to see:
    - A list of validation images needing approval
    - What antibodies are used in an experiment but are not valid, and who used/submitted them (or a list of antibodies that need lab attention) by lab
    - A general way to search for antibodies or targets
    - Direct links to the standards papers on how we are judging validations

Background:
    Given I am logged in as an approver
    And a pending validation image exists

Scenario: List of validation images needing approval
    When I visit my dashboard
    And follow the link to pending validation images
    Then the pending validation image is listed in the table
    And the pending validation image is highlighted
    And the pending validation image links to a detail page

Scenario: Validation image details
    When I visit a validation image page
    Then I should see the validation image
    And I should see the validation caption
    And I should see the validation method
    And I should see the validation species intended for use (mouse or human)
    And I should see a link to the antibody product information

Scenario: Pending validation image approval
    When I visit the pending validation image page
    And I click "Approve"
    Then the validation image should change status to "Approved" and be reflected visually
    And a status change email should be sent to the submitter

Scenario: Pending validation image rejection
    When I visit the pending validation image page
    And I click "Reject"
    Then there should be a place for me to comment
    When I comment and click "Reject"
    Then the validation image should change status to "Rejected" and be reflected visually
    And a status change email should be sent to the submitter
    And the status change email should include the comment

