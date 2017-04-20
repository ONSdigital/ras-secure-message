Feature: Message get by ID Endpoint

  Scenario: Respondent sends multiple messages and retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the respondent wants to get their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Internal user sends multiple messages and retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Internal user wants to get their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Respondent sends multiple messages and internal user retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the internal user wants to get their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Respondent wants to get their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels
