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
      And a success status code (200) is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario: A respondent sends a message to group. A specific internal user marks it as read .Reads message should not have UNREAD label
    Given sending from respondent to internal group
      And  the message is sent V2
      And  the user is set as internal specific user
      And  the message is read V2
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified V2
    When   the message is read V2
    Then the response message does not have the label 'UNREAD'