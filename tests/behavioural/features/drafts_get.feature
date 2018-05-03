Feature: Get Drafts

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario: A respondent saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from respondent to internal bres user
      And '5' drafts are sent
      And the draft is sent as a message
    When  drafts are read
    Then  a success status code (200) is returned
      And '4' messages are returned

  Scenario: An internal user saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from internal bres user to respondent
      And '5' drafts are sent
      And the draft is sent as a message
    When  drafts are read
    Then  a success status code (200) is returned
      And '4' messages are returned

  Scenario: A Respondent saves multiple drafts , another user attempts to read drafts
    Given sending from respondent to internal bres user
      And  '20' drafts are sent
      And the user is set as alternative respondent
    When  drafts are read
    Then  a success status code (200) is returned
      And '0' messages are returned

  Scenario: An internal user saves multiple drafts , another user attempts to read drafts
    Given sending from internal bres user to respondent
      And  '20' drafts are sent
      And  the user is set as alternative respondent
    When  drafts are read
    Then  a success status code (200) is returned
      And  '0' messages are returned

  Scenario: Respondent saves multiple drafts , internal user attempts to get drafts
    Given sending from respondent to internal bres user
     And   '5' drafts are sent
    When the user is set as internal
      And drafts are read
    Then  a success status code (200) is returned
      And  '0' messages are returned

  Scenario: An internal user saves multiple drafts , respondent attempts to get drafts
    Given sending from internal bres user to respondent
     And   '5' drafts are sent
    When the user is set as respondent
      And drafts are read
    Then  a success status code (200) is returned
      And  '0' messages are returned
