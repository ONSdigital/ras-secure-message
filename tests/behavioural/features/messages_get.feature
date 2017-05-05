Feature: Message get by ID Endpoint

  Scenario: Respondent sends multiple messages and retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the respondent gets their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Internal user sends multiple messages and retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Internal user gets their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Respondent sends multiple messages and internal user retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the Internal user gets their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Respondent gets their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels

 Scenario: As an external user I would like to be able to view a list of messages
    Given multiple messages have been sent to an external user
    When the external user navigates to their messages
    Then messages are displayed

 Scenario: internal - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is displayed to an internal user
    When the internal user opens the message
    Then the status of the message changes to from 'unread' to 'read' for all internal users

  Scenario: internal - as an internal user I want to be able to change my message from read to unread
    Given a message with the status 'read' is displayed to an internal user
    When the user chooses to edit the status from 'read' to 'unread'
    Then the status of that message changes to 'unread' for all internal users
