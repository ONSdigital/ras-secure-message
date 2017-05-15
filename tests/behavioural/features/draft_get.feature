Feature: Get draft by id

  Scenario: User requests draft
    Given a user requests a valid draft
    When the user requests the draft
    Then the draft is returned
    And a success response is returned

  Scenario: User requests draft that does not exist
    Given a user wants a draft that does not exist
    When the user requests the draft
    Then the user receives a draft not found response

  @ignore
  Scenario: User requests draft not authorised to view
    Given a user is not authorised
    When the user requests the draft
    Then the user is forbidden from viewing draft
