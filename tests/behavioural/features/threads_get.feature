Feature: Get threads list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given new sending from respondent to internal
      And new the message is sent
      And new the message is sent
      And new the message is sent
   When new the threads are read
    Then  a success status code (200) is returned
      And new '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal , internal attempts to read them
    Given new sending from respondent to internal
      And new '3' messages are sent
     When   new the user is set as internal
      And new the threads are read
    Then  a success status code (200) is returned
      And new '3' messages are returned


  Scenario: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given new sending from respondent to internal
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

      And   new the thread_id is set to empty
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

      And   new the thread_id is set to empty
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

   When new the threads are read
    Then  a success status code (200) is returned
      And new '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given new sending from respondent to internal
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

      And   new the thread_id is set to empty
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

      And   new the thread_id is set to empty
      And new the message is sent
      And   new the thread id is set to the last returned thread id
      And new the message is sent

    When  new the user is set as internal
      And new the threads are read
    Then  a success status code (200) is returned
      And new '3' messages are returned


  Scenario: There are 3 conversations between respondent and internal each with 2  messages and a draft, validate most recent message returned for each
    Given new sending from respondent to internal
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

      And new the thread_id is set to empty
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

      And new the thread_id is set to empty
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

   When new the threads are read
    Then  a success status code (200) is returned
      And  new '3' messages are returned
          # Drafts added last
      And new '3' messages have a 'DRAFT' label

  Scenario: There are 3 conversations between an internal user and respondent each with 2  messages and a draft, validate most recent message returned for each
    Given new sending from internal to respondent
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

      And new the thread_id is set to empty
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

      And new the thread_id is set to empty
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is sent
      And new the thread id is set to the last returned thread id
      And new the message is saved as draft

   When new the threads are read
    Then  a success status code (200) is returned
      And  new '3' messages are returned
      # Drafts added last
      And new '3' messages have a 'DRAFT' label



