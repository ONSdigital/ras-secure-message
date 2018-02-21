Feature: Get Drafts V2

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario Outline: A respondent saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from respondent to internal <user>
      And '5' drafts are sent V2
      And the message is read V2
      And the draft is sent as a message V2
    When  drafts are read V2
    Then  a success status code (200) is returned
      And '4' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: An internal user saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from internal <user> to respondent
      And '5' drafts are sent V2
      And the message is read V2
      And the draft is sent as a message V2
    When  drafts are read V2
    Then  a success status code (200) is returned
      And '4' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: A respondent saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given sending from respondent to internal <user>
      And '5' drafts are sent V2
      And the message is read V2
      And the draft is sent as a message V2
    When  messages are read V2
    Then  a success status code (200) is returned
      And '5' messages are returned
      And '4' messages have a 'DRAFT' label
      And '1' messages have a 'SENT' label

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: An internal user saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given sending from internal <user> to respondent
      And '5' drafts are sent V2
      And the message is read V2
      And the draft is sent as a message V2
    When  messages are read V2
    Then  a success status code (200) is returned
      And '5' messages are returned
      And '4' messages have a 'DRAFT' label
      And '1' messages have a 'SENT' label

    Examples: user type
    | user        |
    | specific user |
    | group        |


