Feature: Checking correct labels for messages are added & deleted

  Background: Reset database
    Given prepare for tests using 'mock' services

   Scenario: A respondent sends a message the internal user marks it as READ
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
     When the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
      And  the message is read
     Then the response message does not have the label 'UNREAD'
      And a success status code (200) is returned

  Scenario: An internal user sends a message the internal user marks it as READ
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
     When the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
      And  the message is read
     Then the response message does not have the label 'UNREAD'
      And a success status code (200) is returned

  Scenario: A respondent sends a message the internal user marks it as READ then UNREAD
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
      And  the message is read
     When  a label of 'UNREAD' is to be added
      And  the message labels are modified
      And  the message is read
     Then the response message has the label 'UNREAD'
      And the response message has the label 'INBOX'
      And the response message should a label count of '2'
      And a success status code (200) is returned


  Scenario: An internal user sends a message the internal user marks it as READ then UNREAD
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
      And  the message is read
     When  a label of 'UNREAD' is to be added
      And  the message labels are modified
      And  the message is read
     Then the response message has the label 'UNREAD'
      And the response message has the label 'INBOX'
      And the response message should a label count of '2'
      And a success status code (200) is returned



  Scenario: A respondent sends a message the internal user attempts to modify a label without specifying which label
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
    When the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without specifying which label
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
    When the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label without an expected action
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'INBOX' has unknown action
    When the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without an expected action
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'INBOX' has unknown action
    When the message labels are modified
    Then a bad request status code (400) is returned

   Scenario: A respondent sends a message the internal user attempts to modify a label with an invalid name
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'MyMadeUpLabelName' is to be added
    When the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label with an invalid name
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'MyMadeUpLabelName' is to be added
    When the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label using an incorrect message id
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'UNREAD' is to be removed
    When  the message labels are modified on msg id '1234'
    Then a not found status code (404) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label using an incorrect message id
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'UNREAD' is to be removed
    When  the message labels are modified on msg id '1234'
      Then a not found status code (404) is returned

  Scenario: Respondent sends a message to an internal user an alternative respondent attempts to modify its labels
      Given sending from respondent to internal bres user
        And  the message is sent
      When  the user is set as alternative respondent
        And a label of 'UNREAD' is to be removed
        And the message labels are modified
      Then a bad request status code (400) is returned

  Scenario: An internal user sends a mesage to a respondent user an alternative respondent attempts to modify its labels
      Given sending from internal bres user to respondent
        And  the message is sent
      When  the user is set as alternative respondent
        And a label of 'UNREAD' is to be removed
        And the message labels are modified
      Then a bad request status code (400) is returned
