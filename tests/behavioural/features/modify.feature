Feature: Checking correct labels for messages are added & deleted

  Scenario: add the "archived" label to the message
    Given a valid message is sent
    When the message is archived
    Then check message is marked as archived

  Scenario: deleting the "archived" label from a given message
    Given the message is archived
    When the message is unarchived
    Then check message is not marked as archived

  Scenario: add the "unread" label to the message
    Given a message has been read
    When the message is marked unread
    Then check message is marked unread

  Scenario: deleting the "unread" level from a given message
    Given a valid message is sent
    When the message is marked read
    Then check message is not marked unread
    And message read date should be set