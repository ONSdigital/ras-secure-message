Feature: Checking correct labels for messages are added & deleted

  Background: Reset database
    Given database is reset

  Scenario: modifying the status of the message to "archived"
    Given a valid message is sent
    When the message is archived
    Then check message is marked as archived

  Scenario: deleting the "archived" label from a given message
    Given the message is archived
    When the message is unarchived
    Then check message is not marked as archived

  Scenario: Modifying the status of the message to "unread"
    Given a message has been read
    When the message is marked unread
    Then check message is marked unread

  Scenario: modifying the status of the message so that "unread" is removed
    Given a valid message is sent
    When the message is marked read
    Then check message is not marked unread
    And message read date should be set

  Scenario: validating a request where there is no label provided
    Given a message is sent
    When the label is empty
    Then a Bad Request error is returned

  Scenario: validating a request where there is no action provided
    Given a message is sent
    When the action is empty
    Then a Bad Request 400 error is returned

  Scenario: validating a request where there in an invalid label provided
    Given a message is sent
    When an invalid label is provided
    Then display a Bad Request is returned

  Scenario: validating a request where there in an invalid action provided
    Given a message is sent
    When an invalid action is provided
    Then show a Bad Request is returned

  Scenario: validating a request where there in an unmodifiable label is provided
    Given a message is sent
    When an unmmodifiable label is provided
    Then a Bad Request is displayed to the user

  @ignore
 Scenario: internal - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is shown to an internal user
    When the internal user opens the message
    Then the status of the message changes from 'unread' to 'read' for all internal users that have access to that survey

  @ignore
  Scenario: As an external user - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is shown to an external user
    When the external user opens the message
    Then the status of the message changes to from unread to read

   Scenario: If an incorrect message id is requested by the user return a 404 error
    Given a user requests a message with a invalid message id
    When it is searched for
    Then a 404 error code is returned