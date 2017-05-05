Feature: Message get by ID Endpoint

  Scenario: Retrieve a message with correct message ID
    Given there is a message to be retrieved
    When the get request is made with a correct message id
    Then a 200 HTTP response is returned

  Scenario: Retrieve a message with incorrect message ID
    Given there is a message to be retrieved
    When the get request has been made with an incorrect message id
    Then a 404 HTTP response is returned

  Scenario: Respondent sends message and retrieves the same message with it's labels
    Given a respondent sends a message
    When the respondent wants to see the message
    Then the retrieved message should have the label SENT

  Scenario: Internal user sends message and retrieves the same message with it's labels
    Given an internal user sends a message
    When the internal user wants to see the message
    Then the retrieved message should have the label SENT

  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
    Given an internal user sends a message
    When the respondent wants to see the message
    Then the retrieved message should have the labels INBOX and UNREAD

  Scenario: Respondent sends message and internal user retrieves the same message with it's labels
    Given a respondent sends a message
    When the internal user wants to see the message
    Then the retrieved message should have the labels INBOX and UNREAD 

 Scenario: internal - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is displayed to an internal user
    When the internal user opens the message
    Then the status of the message changes to from 'unread' to 'read' for all internal users

  Scenario: internal - as an internal user I want to be able to change my message from read to unread
    Given a message with the status 'read' is displayed to an internal user
    When the user chooses to edit the status from 'read' to 'unread'
    Then the status of that message changes to 'unread' for all internal users

  Scenario: As an external user - message status automatically changes to read - on opening message
    Given a message with the status 'unread' is displayed to an external user
    When the external user opens the message
    Then the status of the message changes to from 'unread' to 'read'

  Scenario: As an external user I want to be able to change the status of my message from read to unread
    Given a message with the status 'read' is displayed to an external user
    When the external user chooses to edit the status from 'read' to 'unread'
    Then the status of that message changes to 'unread'
