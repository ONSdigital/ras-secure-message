Feature: Get Messages list Endpoint

  Background: Reset database
    Given database is reset
    And using mock party service
    And using mock case service

  Scenario: A Respondent sends multiple messages, Internal user reads them confirm correct count seen
    Given new sending from respondent to internal
      And  new '5' messages are sent
    When new messages are read
    Then  new '5' messages are returned

  Scenario: An internal user sends multiple messages, Internal user reads them confirm correct count seen
    Given new sending from internal to respondent
    And  new '5' messages are sent
    When new messages are read
    Then  new '5' messages are returned

  Scenario: A Respondent sends multiple messages and reads them to confirm all have SENT labels
    Given new sending from respondent to internal
      And  new '5' messages are sent
    When new messages are read
    Then  new all response messages have the label 'SENT'

  Scenario: An internal user sends multiple messages and reads them to confirm all have SENT labels
    Given new sending from internal to respondent
      And  new '5' messages are sent
    When new messages are read
    Then  new all response messages have the label 'SENT'

  Scenario: A Respondent sends multiple messages, and Internal user reads them confirm all have INBOX and UNREAD  labels
    Given new sending from respondent to internal
      And  new '5' messages are sent
      And new the user is set as internal
    When new messages are read
    Then  new all response messages have the label 'INBOX'
      And new all response messages have the label 'UNREAD'

  Scenario: An internal user sends multiple messages, and a respondent user reads them confirm all have INBOX and UNREAD  labels
    Given new sending from internal to respondent
      And  new '5' messages are sent
      And new the user is set as respondent
    When new messages are read
    Then  new all response messages have the label 'INBOX'
      And new all response messages have the label 'UNREAD'

   Scenario: A Respondent sends multiple messages against two rus, Internal user reads them confirm correct count seen
    Given new sending from respondent to internal
      And  new '5' messages are sent
      And  new ru set to alternate ru
      And  new '3' messages are sent
    When new the user is set as internal
     And new ru set to default ru
     And new messages are read using current 'ru_id'
    Then  new '5' messages are returned

  Scenario: An internal user sends multiple messages against two rus, Respondent user reads them confirm correct count seen
    Given new sending from internal to respondent
      And  new '5' messages are sent
      And  new ru set to alternate ru
      And  new '3' messages are sent
    When new the user is set as internal
     And new ru set to default ru
     And new messages are read using current 'ru_id'
    Then  new '5' messages are returned

   Scenario: A Respondent sends multiple messages against two surveys, Internal user reads them confirm correct count seen
    Given new sending from respondent to internal
      And  new '5' messages are sent
      And  new survey is set to alternate survey
      And  new '3' messages are sent
    When new the user is set as internal
     And new survey set to default survey
     And new messages are read using current 'survey'
    Then  new '5' messages are returned

  Scenario: An internal user sends multiple messages against two surveys, respondent reads them confirm correct count seen
    Given new sending from internal to respondent
      And  new '5' messages are sent
      And  new survey is set to alternate survey
      And  new '3' messages are sent
    When new the user is set as respondent
     And new survey set to default survey
     And new messages are read using current 'survey'
    Then  new '5' messages are returned

  Scenario: A respondent user sends multiple messages against two collection cases, Internal user  reads them confirm correct count seen
    Given new sending from respondent to internal
      And  new '5' messages are sent
      And  new collection case is set to alternate collection case
      And  new '3' messages are sent
    When new the user is set as internal
     And new collection case set to default collection case
     And new messages are read using current 'collection_case'
    Then  new '5' messages are returned


   Scenario: An internal user sends multiple messages against two collection cases, Respondent  reads them confirm correct count seen
    Given new sending from internal to respondent
      And  new '5' messages are sent
      And  new collection case is set to alternate collection case
      And  new '3' messages are sent
    When new the user is set as respondent
     And new collection case set to default collection case
     And new messages are read using current 'collection_case'
    Then  new '5' messages are returned

  Scenario: A respondent user sends multiple messages against two collection exercises, Internal user  reads them confirm correct count seen
    Given new sending from respondent to internal
      And  new '5' messages are sent
      And  new collection exercise is set to alternate collection exercise
      And  new '3' messages are sent
    When new the user is set as internal
     And new collection exercise set to default collection exercise
     And new messages are read using current 'collection_exercise'
    Then  new '5' messages are returned


   Scenario: An internal user sends multiple messages against two collection exercises, Respondent  reads them confirm correct count seen
    Given new sending from internal to respondent
      And  new '5' messages are sent
      And  new collection exercise is set to alternate collection exercise
      And  new '3' messages are sent
    When new the user is set as respondent
     And new collection exercise set to default collection exercise
     And new messages are read using current 'collection_exercise'
    Then  new '5' messages are returned

 @ignore
 Scenario: Respondent creates multiple draft messages and Respondent retrieves the list of draft messages 
    Given a Respondent creates multiple draft messages 
    When the Respondent gets their draft messages 
    Then the retrieved messages should all have draft labels
 @ignore
 Scenario: Respondent creates multiple draft messages and Internal user retrieves a list of messages 
    Given a Respondent creates multiple draft messages 
    When the Internal user gets their messages
    Then the retrieved messages should not have DRAFT_INBOX labels
  
 @ignore
  Scenario Outline: Respondent gets messages with various labels options
    Given the user is internal
    And multiple messages sent to respondent
    When respondent gets messages with label <labels>
    Then messages returned should have one of the labels <labels>

  Examples: Parameters
    |labels  |
    |INBOX   |
    |UNREAD  |
 @ignore
  Scenario: A respondent sends multiple messages , Another respondent should not see any
    Given a Internal user sends multiple messages
    When A different external user requests all messages
    Then a success status code (200) is returned
    And  No messages should be returned


  @ignore
  Scenario Outline: User provides parameters that are invalid
    Given parameter <param> has value <value>
    When user gets messages using the parameters
    Then a not found status code (404) is returned

  Examples: Parameters
    |param         | value |
    |limit         | string|
    |page          | string|
    |survey        | NotASurvey |
    |labels        | NotALabel  |

  @ignore
  Scenario Outline: User provides parameters that are too large
    Given parameter <param> has value <value>
    When user gets messages using the parameters
    Then a bad request status code (400) is returned

  Examples: Parameters
    |param         | value |
    |ru_id         | LongerThan11Chars |
    |labels        | INBOX-SENT-ARCHIVED-DRAFT-INBOX-SENT-ARCHIVED-DRAFT |


