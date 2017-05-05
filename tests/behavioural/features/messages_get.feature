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

 Scenario: 
    Given multiple messages have been sent to an External user
    When the External user navigates to their messages
    Then messages are displayed
    
    
