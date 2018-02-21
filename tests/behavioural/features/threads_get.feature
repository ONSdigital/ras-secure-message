Feature: Get threads list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal bres user
      And the message is sent
      And the message is sent
      And the message is sent
   When the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal bres user
      And '3' messages are sent
     When   the user is set as internal
      And the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal bres user
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
    Given sending from respondent to internal bres user
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
    Given sending from respondent to internal bres user
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
    Given sending from internal bres user to respondent
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



