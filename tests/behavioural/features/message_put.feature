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
    Then a bad request status code (400) is returned

  Scenario: validating a request where there is no action provided
    Given a message is sent
    When the action is empty
    Then a bad request status code (400) is returned

  Scenario: validating a request where there in an invalid label provided
    Given a message is sent
    When an invalid label is provided
    Then a bad request status code (400) is returned

  Scenario: validating a request where there in an invalid action provided
    Given a message is sent
    When an invalid action is provided
    Then a bad request status code (400) is returned

  Scenario: validating a request where an unmodifiable label is provided
    Given a message is sent
    When an unmodifiable label is provided
    Then a bad request status code (400) is returned

  Scenario: internal - as an internal user I want to be able to change my message from read to unread
    Given a message with the status read is displayed to an internal user
    When the internal user chooses to edit the status from read to unread
    Then the status of that message changes to unread for all internal users that have access to that survey

  Scenario: internal - as an internal user I want to be able to change my message from unread to read
    Given a message with the status unread is displayed to an internal user
    When the internal user chooses to edit the status from unread to read
    Then the status of that message changes to read for all internal users that have access to that survey

  Scenario: external  - as an external user I want to be able to change my message from read to unread
    Given a message with the status read is displayed to an external user
    When the external user chooses to edit the status from read to unread
    Then the status of that message changes to unread

  Scenario: external - as an external user I want to be able to change my message from unread to read
    Given a message with the status unread is displayed to an external user
    When the external user chooses to edit the status from unread to read
    Then the status of that message changes to read

  Scenario: If an incorrect message id is requested by the user return a 404 error
    Given a user requests a message with a invalid message id
    When it is searched for
    Then a not found status code (404) is returned

  Scenario: If an incorrect message id is requested by the user return a 404 error
    Given a user requests a message with a invalid message id
    When it is searched for
    Then a not found status code (404) is returned

  Scenario: As a user I should receive an error if I attempt to mark a message as read that is not in my inbox
    Given a message is sent from internal
    When the message is marked read
    Then a bad request status code (400) is returned
    