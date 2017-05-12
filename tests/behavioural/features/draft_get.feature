Feature: Get Draft By ID

  @ignore
  Scenario: As an internal user I want to be able to view a message from my drafts
    Given an internal user has created and saved a draft message
    When the internal user navigates to draft messages and opens the draft message
    Then the draft message should be displayed

  @ignore
  Scenario: As an External user I would like to be able to view a message from drafts
    Given an external user has created and saved a draft message
    When the external user navigates to draft messages and opens the draft message
    Then the draft message should be displayed