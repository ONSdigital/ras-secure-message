Feature: Checking correct labels for messages are added & deleted

 Background: Reset database
    Given database is reset
    And using mock party service
    And using mock case service

  Scenario: A Respondent  modifies the archive status or a message to archived
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the message is read
      And  new a label of 'ARCHIVE' is to be added
    When  new the message labels are modified
      And  new the message is read
    Then new the response message has the label 'ARCHIVE'

  Scenario: An internal user modifies the archive status or a message to archived
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the message is read
      And  new a label of 'ARCHIVE' is to be added
    When  new the message labels are modified
      And  new the message is read
    Then new the response message has the label 'ARCHIVE'

  Scenario: A Respondent removes an archived status from a message
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the message is read
      And  new a label of 'ARCHIVE' is to be added
      And  new the message labels are modified
      And  new the message is read
    When  new a label of 'ARCHIVE' is to be removed
      And  new the message labels are modified
      And  new the message is read
    Then new the response message does not have the label 'ARCHIVE'

  Scenario: An internal user removes an archived status from a message
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the message is read
      And  new a label of 'ARCHIVE' is to be added
      And  new the message labels are modified
      And  new the message is read
    When  new a label of 'ARCHIVE' is to be removed
      And  new the message labels are modified
      And  new the message is read
    Then new the response message does not have the label 'ARCHIVE'

   Scenario: A respondent sends a message the internal user marks it as READ
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
     When new the message is read
      And  new a label of 'UNREAD' is to be removed
      And  new the message labels are modified
      And  new the message is read
     Then new the response message does not have the label 'UNREAD'

  Scenario: An internal user sends a message the internal user marks it as READ
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
     When new the message is read
      And  new a label of 'UNREAD' is to be removed
      And  new the message labels are modified
      And  new the message is read
     Then new the response message does not have the label 'UNREAD'

  Scenario: A respondent sends a message the internal user marks it as READ then UNREAD
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
      And  new a label of 'UNREAD' is to be removed
      And  new the message labels are modified
      And  new the message is read
     When  new a label of 'UNREAD' is to be added
      And  new the message labels are modified
      And  new the message is read
     Then new the response message has the label 'UNREAD'
      And new the response message has the label 'INBOX'
      And new the response message should a label count of '2'


  Scenario: An internal user sends a message the internal user marks it as READ then UNREAD
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
      And  new a label of 'UNREAD' is to be removed
      And  new the message labels are modified
      And  new the message is read
     When  new a label of 'UNREAD' is to be added
      And  new the message labels are modified
      And  new the message is read
     Then new the response message has the label 'UNREAD'
      And new the response message has the label 'INBOX'
      And new the response message should a label count of '2'



  Scenario: A respondent sends a message the internal user attempts to modify a label without specifying which label
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
    When new the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without specifying which label
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
    When new the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label without an expected action
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
      And new a label of 'INBOX' has unknown action
    When new the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label without an expected action
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
      And new a label of 'INBOX' has unknown action
    When new the message labels are modified
    Then a bad request status code (400) is returned

   Scenario: A respondent sends a message the internal user attempts to modify a label with an invalid name
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
      And new a label of 'MyMadeUpLabelName' is to be added
    When new the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label with an invalid name
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
      And new a label of 'MyMadeUpLabelName' is to be added
    When new the message labels are modified
    Then a bad request status code (400) is returned


  Scenario: A respondent sends a message the internal user attempts to modify a label using an incorrect message id
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
      And new a label of 'UNREAD' is to be removed
    When  new the message labels are modified on msg id '1234'
    Then a not found status code (404) is returned


  Scenario: An internal user sends a message the internal user attempts to modify a label using an incorrect message id
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
      And new a label of 'UNREAD' is to be removed
    When  new the message labels are modified on msg id '1234'
      Then a not found status code (404) is returned

  Scenario: Respondent sends a message to an internal user an alternative respondent attempts to modify its labels
      Given new sending from respondent to internal
        And  new the message is sent
      When  new the user is set as alternative respondent
        And new a label of 'UNREAD' is to be removed
        And new the message labels are modified
      Then a bad request status code (400) is returned

  Scenario: An internal user sends a mesage to a respondent user an alternative respondent attempts to modify its labels
      Given new sending from internal to respondent
        And  new the message is sent
      When  new the user is set as alternative respondent
        And new a label of 'UNREAD' is to be removed
        And new the message labels are modified
      Then a bad request status code (400) is returned