Feature: Get draft by id

  @ignore
  Scenario: User requests draft
    Given a user requests a valid draft
    When the user requests a draft
    Then the draft is returned
    And a success response is returned

  @ignore
  Scenario: User requests draft not authorised to view
    Given a user is not authorised
    When draft is requested
    Then the user is forbidden from viewing draft

  @ignore
  Scenario: User requests draft that does not exist
    Given a user wants a draft that does not exist
    When the user requests the draft
    Then the user receives a bad request response
