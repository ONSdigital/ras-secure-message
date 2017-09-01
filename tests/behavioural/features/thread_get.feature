Feature: Get thread by id Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation, validate respondent sees all messages
    Given new sending from respondent to internal
      And   new the message is sent
      And   new the user is set as internal
      And   new the from is set to internal
      And   new the to is set to respondent
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the user is set as respondent
      And   new the from is set to respondent
      And   new the to is set to internal
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
    When new the thread is read
    Then new '3' messages are returned
      And new '2' messages have a 'SENT' label
      And new '1' messages have a 'INBOX' label

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation, validate internal user sees all messages
    Given new sending from respondent to internal
      And   new the message is sent
      And   new the user is set as internal
      And   new the from is set to internal
      And   new the to is set to respondent
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the user is set as respondent
      And   new the from is set to respondent
      And   new the to is set to internal
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the user is set as internal
    When new the thread is read
    Then new '3' messages are returned
      And new '1' messages have a 'SENT' label
      And new '2' messages have a 'INBOX' label

  Scenario: Respondent and internal user have a conversation including drafts and respondent retrieves the conversation, validate respondent sees all messages
    Given new sending from respondent to internal
      And   new the message is sent
      And   new the user is set as internal
      And   new the from is set to internal
      And   new the to is set to respondent
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the user is set as respondent
      And   new the from is set to respondent
      And   new the to is set to internal
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is saved as draft
    When new the thread is read
    Then new '3' messages are returned
      And new '1' messages have a 'SENT' label
      And new '1' messages have a 'INBOX' label
      And new '1' messages have a 'DRAFT' label

  Scenario: Respondent and internal user have a conversation including drafts and respondent retrieves the conversation, validate internal does not see draft
    Given new sending from respondent to internal
      And   new the message is sent
      And   new the user is set as internal
      And   new the from is set to internal
      And   new the to is set to respondent
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the user is set as respondent
      And   new the from is set to respondent
      And   new the to is set to internal
      And   new the message is read
      And   new the thread id is set to the last returned thread id
      And   new the message is saved as draft
      And   new the user is set as internal
    When new the thread is read
    Then new '2' messages are returned
      And new '1' messages have a 'SENT' label
      And new '1' messages have a 'INBOX' label
      And new '0' messages have a 'DRAFT_INBOX' label

    # 3 messages in first conversation , 2 in second
  Scenario: Respondent and internal user have two conversations respondent retrieves one conversation, validate respondent sees correct messages
    Given new sending from respondent to internal
      And   new the message is sent
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the thread_id is set to empty
      And   new the message is sent
      And   new the thread id is set to the last returned thread id
      And   new the message is sent
      And   new the thread id is set to that from response '0'
      And   new the thread is read
    Then new '3' messages are returned
      And new '3' messages have a 'SENT' label


  Scenario:Respondent tries to retrieve a conversation that does not exist
    Given new sending from respondent to internal
    When new the thread_id is set to 'DoesNotExist'
     And  new the thread is read
    Then a not found status code (404) is returned

  Scenario:Internal user tries to retrieve a conversation that does not exist
    Given new sending from internal to respondent
    When new the thread_id is set to 'DoesNotExist'
     And  new the thread is read
    Then a not found status code (404) is returned
