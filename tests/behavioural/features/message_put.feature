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

 Scenario: internal - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is displayed to an internal user
    When the internal user opens the message
    Then the status of the message changes to from 'unread' to 'read' for all internal users that have access to that work group

  Scenario Outline: internal - as an internal user I want to be able to change my message from read to unread
    Given a message with the status <message status> is displayed to an internal user
    When the user chooses to edit the status from <message status> to (new status>
    Then the status of that message changes to <new status> for all internal users that have access to that work group
    
  Examples: Status
    |message status | new status |
    |read           | unread     |
    |unread         | read       |

  Scenario: As an external user - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is displayed to an external user
    When the external user opens the message
    Then the status of the message changes to from 'unread' to 'read'

  Scenario Outline: external - as an external user I want to be able to change my message from read to unread
    Given a message with the status <message status> is displayed to an external user
    When the user chooses to edit the status from <message status> to (new status>
    Then the status of that message changes to <new status>
    
  Examples: Status
    |message status | new status |
    |read           | unread     |
    |unread         | read       |

  Scenario: As an internal user I want to be able to edit a message from my drafts
    Given an internal user has opened a previously saved draft message
    When the internal user edits the content of the message and saves it as a draft
    Then the original draft message is replaced by the edited version

  Scenario: As an External user I would like to be able to edit a message from drafts
    Given an external user has opened a previously saved draft message
    When the external user edits the content of the message and saves it as a draft
    Then the original draft message is replaced by the edited version
