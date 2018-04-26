Feature: Get threads list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal user
      And the message is sent
      And the message is sent
      And the message is sent
   When the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal user
      And '3' messages are sent
     When   the user is set as internal
      And the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal user
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
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given sending from respondent to internal user
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
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2  messages and a draft, validate most recent message returned for each
    Given sending from respondent to internal user
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

      And the thread_id is set to empty
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

      And the thread_id is set to empty
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

   When the threads are read
    Then  a success status code (200) is returned
      And  '3' messages are returned
          # Drafts added last
      And '3' messages have a 'DRAFT' label

  Scenario: There are 3 conversations between an internal user and respondent each with 2  messages and a draft, validate most recent message returned for each
    Given sending from internal user to respondent
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

      And the thread_id is set to empty
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

      And the thread_id is set to empty
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is saved as draft

   When the threads are read
    Then  a success status code (200) is returned
      And  '3' messages are returned
      # Drafts added last
      And '3' messages have a 'DRAFT' label

  Scenario: A respondent sends a very long message, the internal user sees a 100 character summary in their inbox
    Given sending from internal user to respondent
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
