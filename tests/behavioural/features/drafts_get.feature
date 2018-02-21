Feature: Get Drafts

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario: A respondent saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from respondent to internal bres user
      And '5' drafts are sent
      And the message is read
      And the draft is sent as a message
    When  drafts are read
    Then  a success status code (200) is returned
      And '4' messages are returned

  Scenario: An internal user saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given sending from internal bres user to respondent
      And '5' drafts are sent
      And the message is read
      And the draft is sent as a message
    When  drafts are read
    Then  a success status code (200) is returned
      And '4' messages are returned

  Scenario: A respondent saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given sending from respondent to internal bres user
      And '5' drafts are sent
      And the message is read
      And the draft is sent as a message
    When  messages are read
    Then  a success status code (200) is returned
      And '5' messages are returned
      And '4' messages have a 'DRAFT' label
      And '1' messages have a 'SENT' label

  Scenario: An internal user saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given sending from internal bres user to respondent
      And '5' drafts are sent
      And the message is read
      And the draft is sent as a message
    When  messages are read
    Then  a success status code (200) is returned
      And '5' messages are returned
      And '4' messages have a 'DRAFT' label
      And '1' messages have a 'SENT' label


  Scenario: A respondent sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given sending from respondent to internal bres user
      And  '23' drafts are sent
     When drafts are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: An internal user sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given sending from respondent to internal bres user
      And  '23' drafts are sent
     When drafts are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And '3' messages are returned

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

   Scenario: Respondent saves multiple drafts with two collection cases , validate retrieves correct count based on collection case
    Given sending from respondent to internal bres user
     And   '5' drafts are sent
     And   collection case is set to alternate collection case
     And   '7' drafts are sent
    When  collection case set to default collection case
     And   drafts are read using current 'collection_case'
    Then  a success status code (200) is returned
      And  '5' messages are returned


  Scenario: Internal user saves multiple drafts with two collection cases , validate retrieves correct count based on collection case
    Given sending from internal bres user to respondent
     And   '5' drafts are sent
     And   collection case is set to alternate collection case
     And   '7' drafts are sent
    When  collection case set to default collection case
     And   drafts are read using current 'collection_case'
    Then  a success status code (200) is returned
      And  '5' messages are returned

   Scenario: Respondent saves multiple drafts with two collection exercises , validate retrieves correct count based on collection exercise
    Given sending from respondent to internal bres user
     And   '5' drafts are sent
     And   collection exercise is set to alternate collection exercise
     And   '7' drafts are sent
    When  collection exercise set to default collection exercise
     And   drafts are read using current 'collection_exercise'
    Then  a success status code (200) is returned
      And  '5' messages are returned

  Scenario: Internal user saves multiple drafts with two collection exercises , validate retrieves correct count based on collection exercise
    Given sending from internal bres user to respondent
     And   '5' drafts are sent
     And   collection exercise is set to alternate collection exercise
     And   '7' drafts are sent
    When  collection exercise set to default collection exercise
     And   drafts are read using current 'collection_exercise'
    Then  a success status code (200) is returned
      And  '5' messages are returned

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

  @ignore # Test failing as currently intended recipient can view using a DRAFT_INBOX  label  , remove @ignore when fixed
  Scenario: A respondent saves multiple drafts then , the internal user gets messages with DRAFT_INBOX label
    Given sending from respondent to internal bres user
      And '5' drafts are sent
      And the user is set as internal
    When  drafts with a label of  'DRAFT_INBOX' are read
    Then  a success status code (200) is returned
      And '0' messages are returned

  @ignore # Test failing as currently intended recipient can view using a DRAFT_INBOX  label  , remove @ignore when fixed
  Scenario: An internal user saves multiple drafts then , the respondent user gets messages with DRAFT_INBOX label
    Given sending from internal bres user to respondent
      And '5' drafts are sent
      And the user is set as respondent
    When  drafts with a label of  'DRAFT_INBOX' are read
    Then  a success status code (200) is returned
      And '0' messages are returned



