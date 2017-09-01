Feature: Get Drafts

  Background: Reset database
    Given database is reset
    And   using mock party service
    And using mock case service


  Scenario: A respondent saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given new sending from respondent to internal
      And new '5' messages are sent as drafts
      And new the message is read
      And new the draft is sent as a message
    When  new drafts are read
    Then  a success status code (200) is returned
      And new '4' messages are returned

  Scenario: An internal user saves multiple drafts then  posts one , then read drafts , validate correct number returned
    Given new sending from internal to respondent
      And new '5' messages are sent as drafts
      And new the message is read
      And new the draft is sent as a message
    When  new drafts are read
    Then  a success status code (200) is returned
      And new '4' messages are returned

  Scenario: A respondent saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given new sending from respondent to internal
      And new '5' messages are sent as drafts
      And new the message is read
      And new the draft is sent as a message
    When  new messages are read
    Then  a success status code (200) is returned
      And new '5' messages are returned
      And new '4' messages have a 'DRAFT' label
      And new '1' messages have a 'SENT' label

  Scenario: An internal user saves multiple drafts then  posts one , then reads messages , validate correct number returned
    Given new sending from internal to respondent
      And new '5' messages are sent as drafts
      And new the message is read
      And new the draft is sent as a message
    When  new messages are read
    Then  a success status code (200) is returned
      And new '5' messages are returned
      And new '4' messages have a 'DRAFT' label
      And new '1' messages have a 'SENT' label


  Scenario: A respondent sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given new sending from respondent to internal
      And  new '23' drafts are sent
     When new drafts are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And new '3' messages are returned

  Scenario: An internal user sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given new sending from respondent to internal
      And  new '23' drafts are sent
     When new drafts are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And new '3' messages are returned

  Scenario: A Respondent saves multiple drafts , another user attempts to read drafts
    Given new sending from respondent to internal
      And  new '20' drafts are sent
      And new the user is set as alternative respondent
    When  new drafts are read
    Then  a success status code (200) is returned
      And new '0' messages are returned

  Scenario: An internal user saves multiple drafts , another user attempts to read drafts
    Given new sending from internal to respondent
      And  new '20' drafts are sent
      And  new the user is set as alternative respondent
    When  new drafts are read
    Then  a success status code (200) is returned
      And  new '0' messages are returned

   Scenario: Respondent saves multiple drafts with two collection cases , validate retrieves correct count based on collection case
    Given new sending from respondent to internal
     And   new '5' drafts are sent
     And   new collection case is set to alternate collection case
     And   new '7' drafts are sent
    When  new collection case set to default collection case
     And   new drafts are read using current 'collection_case'
    Then  a success status code (200) is returned
      And  new '5' messages are returned


  Scenario: Internal user saves multiple drafts with two collection cases , validate retrieves correct count based on collection case
    Given new sending from internal to respondent
     And   new '5' drafts are sent
     And   new collection case is set to alternate collection case
     And   new '7' drafts are sent
    When  new collection case set to default collection case
     And   new drafts are read using current 'collection_case'
    Then  a success status code (200) is returned
      And  new '5' messages are returned

   Scenario: Respondent saves multiple drafts with two collection exercises , validate retrieves correct count based on collection exercise
    Given new sending from respondent to internal
     And   new '5' drafts are sent
     And   new collection exercise is set to alternate collection exercise
     And   new '7' drafts are sent
    When  new collection exercise set to default collection exercise
     And   new drafts are read using current 'collection_exercise'
    Then  a success status code (200) is returned
      And  new '5' messages are returned

  Scenario: Respondent saves multiple drafts with two collection exercises , validate retrieves correct count based on collection exercise
    Given new sending from internal to respondent
     And   new '5' drafts are sent
     And   new collection exercise is set to alternate collection exercise
     And   new '7' drafts are sent
    When  new collection exercise set to default collection exercise
     And   new drafts are read using current 'collection_exercise'
    Then  a success status code (200) is returned
      And  new '5' messages are returned

  Scenario: Respondent saves multiple drafts , internal user attempts to get drafts
    Given new sending from respondent to internal
     And   new '5' drafts are sent
    When new the user is set as internal
      And new drafts are read
    Then  a success status code (200) is returned
      And  new '0' messages are returned

  Scenario: An internal user saves multiple drafts , respondent attempts to get drafts
    Given new sending from internal to respondent
     And   new '5' drafts are sent
    When new the user is set as respondent
      And new drafts are read
    Then  a success status code (200) is returned
      And  new '0' messages are returned

  Scenario: A respondent saves multiple drafts then , the internal user gets messages with DRAFT_INBOX label
    Given new sending from respondent to internal
      And new '5' messages are sent as drafts
      And new the user is set as internal
    When  new drafts with a label of  'DRAFT_INBOX' are read
    Then  a success status code (200) is returned
      And new '5' messages are returned


  Scenario: An internal user saves multiple drafts then , the respondent user gets messages with DRAFT_INBOX label
    Given new sending from internal to respondent
      And new '5' messages are sent as drafts
      And new the user is set as respondent
    When  new drafts with a label of  'DRAFT_INBOX' are read
    Then  a success status code (200) is returned
      And new '5' messages are returned



