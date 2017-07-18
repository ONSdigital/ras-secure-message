Feature: Get draft by id

  Background: Reset database
    Given database is reset

  Scenario: User requests draft
    Given a user requests a valid draft
    When the user requests the draft
    Then the draft is returned
    And a success response is given

  Scenario: User requests draft that does not exist
    Given a user wants a draft that does not exist
    When the user requests the draft
    Then a 404 error code is returned

  @ignore
  Scenario: User requests draft not authorised to view
    Given a user is not authorised
    When the user requests the draft
    Then the user is forbidden from viewing draft

  Scenario: User is retrieving the etag from the header
    Given there is a draft
    When the user requests the draft
    Then an etag should be sent with the draft
