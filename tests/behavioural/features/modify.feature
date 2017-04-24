Feature: Checking correct labels for messages are added & deleted

  Scenario: add the "archived" label to the message
    Given a valid message is sent
    When an archived label is added
    Then check message has label "archived"

  Scenario: deleting the "archived" label from a given message
    Given an archived label is added
    When the archived label is removed
    Then check message does not have label "archived"

  Scenario: add the "unread" label to the message
    Given a message has been read
    When the unread label is added
    Then check message has label "unread"

  Scenario: deleting the "unread" level from a given message
    Given a valid message is sent
    When the unread label is removed
    Then check message does not have label "unread"