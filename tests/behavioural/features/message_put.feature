Feature: Checking correct labels for messages are added & deleted

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: An internal user sends a message the internal user marks it as READ then UNREAD
    Given sending from internal <user> to respondent
      And  the message is sent
      And  the user is set as respondent
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
     When  a label of 'UNREAD' is to be added
      And  the message labels are modified
      And  the thread is read
     Then the response thread has the label 'UNREAD'
      And the response thread has the label 'INBOX'
      And the response should have a label count of '2'
      And a success status code 200 is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario: A respondent sends a message to group. A specific internal user marks it as read .Reads message should not have UNREAD label
    Given sending from respondent to internal group
      And  the message is sent
      And  the user is set as internal specific user
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
    When   the thread is read
    Then the response thread does not have the label 'UNREAD'

  Scenario: A respondent sends a message the internal user attempts to modify a label without specifying which label
    Given sending from respondent to internal specific user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
    When the message labels are modified
    Then a bad request status code 400 is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without specifying which label
    Given sending from internal specific user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
    When the message labels are modified
    Then a bad request status code 400 is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label without an expected action
    Given sending from respondent to internal specific user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'INBOX' has unknown action
    When the message labels are modified
    Then a bad request status code 400 is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without an expected action
    Given sending from internal specific user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'INBOX' has unknown action
    When the message labels are modified
    Then a bad request status code 400 is returned

   Scenario: A respondent sends a message the internal user attempts to modify a label with an invalid name
    Given sending from respondent to internal specific user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'MyMadeUpLabelName' is to be added
    When the message labels are modified
    Then a bad request status code 400 is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label with an invalid name
    Given sending from internal specific user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'MyMadeUpLabelName' is to be added
    When the message labels are modified
    Then a bad request status code 400 is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label using an incorrect message id
    Given sending from respondent to internal specific user
      And  the message is sent
      And  the user is set as internal
      And  the thread is read
      And a label of 'UNREAD' is to be removed
    When  the message labels are modified on msg id '1234'
    Then a not found status code 404 is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label using an incorrect message id
    Given sending from internal specific user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the thread is read
      And a label of 'UNREAD' is to be removed
    When  the message labels are modified on msg id '1234'
      Then a not found status code 404 is returned

  Scenario: Respondent sends a message to an internal user an alternative respondent attempts to modify its labels
      Given sending from respondent to internal specific user
        And  the message is sent
      When  the user is set as alternative respondent
        And a label of 'UNREAD' is to be removed
        And the message labels are modified
      Then a bad request status code 400 is returned

  Scenario: An internal user sends a mesage to a respondent user an alternative respondent attempts to modify its labels
      Given sending from internal specific user to respondent
        And  the message is sent
      When  the user is set as alternative respondent
        And a label of 'UNREAD' is to be removed
        And the message labels are modified
      Then a bad request status code 400 is returned