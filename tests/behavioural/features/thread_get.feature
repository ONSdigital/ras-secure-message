Feature: Get thread by id Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

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
