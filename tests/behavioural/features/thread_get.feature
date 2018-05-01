Feature: Get thread by id Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation, validate respondent sees all messages
    Given sending from respondent to internal bres user
      And   the message is sent
      And   the user is set as internal
      And   the from is set to internal bres user
      And   the to is set to respondent
      And   the message is read
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the user is set as respondent
      And   the from is set to respondent
      And   the to is set to internal bres user
      And   the message is read
      And   the thread id is set to the last returned thread id
      And   the message is sent
    When the thread is read
    Then '3' messages are returned
      And '2' messages have a 'SENT' label
      And '1' messages have a 'INBOX' label

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation, validate internal user sees all messages
    Given sending from respondent to internal bres user
      And   the message is sent
      And   the user is set as internal
      And   the from is set to internal bres user
      And   the to is set to respondent
      And   the message is read
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the user is set as respondent
      And   the from is set to respondent
      And   the to is set to internal bres user
      And   the message is read
      And   the thread id is set to the last returned thread id
      And   the message is sent
      And   the user is set as internal
    When the thread is read
    Then '3' messages are returned
      And '1' messages have a 'SENT' label
      And '2' messages have a 'INBOX' label

    # 3 messages in first conversation , 2 in second
  Scenario: Respondent and internal user have two conversations respondent retrieves one conversation, validate respondent sees correct messages
    Given sending from respondent to internal bres user
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

  Scenario:Respondent tries to retrieve a conversation that does not exist
    Given sending from respondent to internal bres user
    When the thread_id is set to 'DoesNotExist'
     And  the thread is read
    Then a not found status code (404) is returned

  Scenario:Internal user tries to retrieve a conversation that does not exist
    Given sending from internal bres user to respondent
    When the thread_id is set to 'DoesNotExist'
     And  the thread is read
    Then a not found status code (404) is returned
