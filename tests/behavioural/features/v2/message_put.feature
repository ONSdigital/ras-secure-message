Feature: Checking correct labels for messages are added & deleted V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: An internal user sends a message the internal user marks it as READ then UNREAD
    Given sending from internal <user> to respondent
      And  the message is sent V2
      And  the user is set as respondent
      And  the message is read V2
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified V2
      And  the message is read V2
     When  a label of 'UNREAD' is to be added
      And  the message labels are modified V2
      And  the message is read V2
     Then the response message has the label 'UNREAD'
      And the response message has the label 'INBOX'
      And the response message should a label count of '2'

    Examples: user type
    | user        |
    | specific user |
    | group        |
