Feature: Get threads list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And the message is sent
      And the message is sent
   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal specific user
      And '3' messages are sent
     When   the user is set as internal
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

    When  the user is set as internal
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: A respondent sends a very long message, the internal user sees a 100 character summary in their inbox
    Given sending from internal specific user to respondent
      And the message body is '5000' characters long
      And '1' messages are sent
    When the threads are read
    Then the message bodies are '100' characters or less

  Scenario: There are 50 conversations between respondent and internal user. Internal user gets conversations should see 50
   Given sending from respondent to internal group
    And '50' messages are sent using V2
   When the user is set as internal specific user
    And the threads are read
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 conversations between internal user and respondent. Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent using V2
   When the user is set as respondent
    And the threads are read
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 conversations between internal user and respondent. Alternative Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent using V2
   When the user is set to alternative internal specific user
    And the threads are read
   Then  '50' messages have a 'SENT' label

  Scenario: The respondent attempts to get conversation list with my_conversations argument set. 400 should be returned
    Given the user is set as respondent
    When  the threads are read with my_conversations set true
    Then a bad request status code 400 is returned

  Scenario: There are 10 conversations each from 2 internal users. Internal user gets threads using my conversations, they only see theirs
    Given  sending from internal specific user to respondent
     And  '10' messages are sent using V2
     And  sending from alternate internal specific user to respondent
     And '9' messages are sent using V2
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '9' messages are returned
     And  all messages are from alternate internal specific user

  Scenario: Two internal users in a conversation with a respondent, with my_conversations set true then the last one will see it in conversation list
    Given sending from respondent to internal specific user
      And the message is sent
      And sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And sending from alternate internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '1' messages are returned
     And  all messages are from alternate internal specific user

  Scenario: Two internal users in a conversation with a respondent, with my_conversations set true then the first  one will NOT see it in conversation list
    Given sending from respondent to internal specific user
      And the message is sent
      And sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And sending from alternate internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the user is set as internal specific user
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '0' messages are returned

  Scenario: Respondent sends to Group , internal user should not see them in threads when using my_conversations
      Given sending from respondent to internal group
        And the message is sent
      When  the user is set as internal specific user
        And the threads are read with my_conversations set true
      Then  '0' messages are returned