Feature: Checking correct labels for messages are added & deleted

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
    Given: a message is sent
    When the label is empty
    Then a Bad Request error is returned

  Scenario: validating a request where there is no action provided
    Given: a suitable message is sent
    When the action is empty
    Then a Bad Request 400 error is returned

  Scenario: validating a request where there in an invalid label provided
    Given: a message is sent
    When an invalid label is provided
    Then display a Bad Request is returned

  Scenario: validating a request where there in an invalid action provided
    Given: a message is sent
    When an invalid action is provided
    Then show a Bad Request is returned

  Scenario: validating a request where there in an unmodifiable label is provided
    Given: a message is sent
    When an unmmodifiable label is provided
    Then a Bad Request is displayed to the user