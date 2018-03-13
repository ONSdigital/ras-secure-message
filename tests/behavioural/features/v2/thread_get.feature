Feature: Get thread by id Endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent and internal user have a conversation and respondent retrieves the conversation, validate respondent sees all messages
    Given sending from respondent to internal <user>
      And   the message is sent V2
      And   sending from internal <user> to respondent
      And   the message is read V2
      And   the thread id is set to the last returned thread id
      And   the message is sent V2
      And   sending from respondent to internal <user>
      And   the message is read V2
      And   the thread id is set to the last returned thread id
      And   the message is sent V2
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
      And   the message is sent V2
      And sending from respondent to internal <user>
      And   the message is read V2
      And   the thread id is set to the last returned thread id
      And   the message is sent V2
      And   sending from internal <user> to respondent
      And   the message is read V2
      And   the thread id is set to the last returned thread id
      And   the message is sent V2
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
    Then  a success status code (200) is returned
      And the threads first message body is as was saved

    Examples: user type
    | user        |
    | specific user |
    | group        |
