Feature: Get thread by id Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  # 3 messages in first conversation , 2 in second
  Scenario: Respondent and internal user have two conversations respondent retrieves one conversation, validate respondent sees correct messages
    Given sending from respondent to internal specific user
      And   the message is sent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the thread_id is set to empty
      And   the message is sent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the thread id is set to that from response '0'
      And   the thread is read
    Then '3' messages are returned
      And '3' messages have a 'SENT' label

  Scenario Outline: Respondent and internal user have a conversation and respondent retrieves the conversation, validate respondent sees all messages
    Given sending from respondent to internal <user>
      And   the message is sent
      And   sending from internal <user> to respondent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   sending from respondent to internal <user>
      And   the thread id is set to the last returned thread id
      And   the message is sent
    When the thread is read
    Then '3' messages are returned
      And '2' messages have a 'SENT' label
      And '1' messages have a 'INBOX' label

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: Internal user and Respondent have a conversation and respondent retrieves the conversation, validate internal user sees all messages
    Given sending from internal <user> to respondent
      And   the message is sent
      And sending from respondent to internal <user>
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   sending from internal <user> to respondent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the user is set as respondent
    When the thread is read
    Then '3' messages are returned
      And '1' messages have a 'SENT' label
      And '2' messages have a 'INBOX' label

    Examples: user type
    | user        |
    | specific user |
    | group        |



  Scenario Outline: Respondent sends a message to internal group, validate the entire message body is received
    Given sending from respondent to internal <user>
      And   the message body is '10000' characters long
      And   the message is sent
    When the thread is read
    Then  a success status code 200 is returned
      And the threads first message body is as was saved

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: Respondent sends 15 messages on one thread . When they get thread by id should return the number of messages on the thread
    Given sending from respondent to internal <user>
      And   the message is sent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
    When the thread is read
    Then '15' messages are returned
     And a success status code 200 is returned

      Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: Respondent sends 15 messages on one thread . When the internal user gets the  thread by id should return the number of messages on the thread
    Given sending from respondent to internal <user>
      And   the message is sent
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
      And   the message is sent
    When  the user is set as internal specific user
     And  the thread is read
    Then '15' messages are returned
     And a success status code 200 is returned

      Examples: user type
    | user        |
    | specific user |
    | group        |


   Scenario: an internal user sends  message , another internal reads the thread, should see the sent message
     Given sending from internal specific user to respondent
      And the message is sent
      And the thread id is set to the last returned thread id
     When the user is set to alternative internal specific user
      And the thread is read
     Then '1' messages are returned

    Scenario: a respondent sends  message to a specific internal user , another internal reads the thread, should see the message
     Given sending from respondent to internal specific user
      And the message is sent
      And the thread id is set to the last returned thread id
     When the user is set to alternative internal specific user
      And the thread is read
     Then '1' messages are returned

  Scenario:Respondent tries to retrieve a conversation that does not exist
    Given sending from respondent to internal specific user
    When the thread_id is set to 'DoesNotExist'
     And  the thread is read
    Then a not found status code 404 is returned

  Scenario:Internal user tries to retrieve a conversation that does not exist
    Given sending from internal specific user to respondent
    When the thread_id is set to 'DoesNotExist'
     And  the thread is read
    Then a not found status code 404 is returned
