Feature: Get Messages list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: A Respondent sends multiple messages, Internal user reads them confirm correct count seen
    Given sending from respondent to internal
      And  '5' messages are sent
    When messages are read
    Then  '5' messages are returned

  Scenario: An internal user sends multiple messages, Internal user reads them confirm correct count seen
    Given sending from internal to respondent
      And  '5' messages are sent
    When messages with a label of  'SENT' are read
    Then  '5' messages are returned

  Scenario: A Respondent sends multiple messages and reads them to confirm all have SENT labels
    Given sending from respondent to internal
      And  '5' messages are sent
    When messages are read
    Then  all response messages have the label 'SENT'

  Scenario: An internal user sends multiple messages and reads them to confirm all have SENT labels
    Given sending from internal to respondent
      And  '5' messages are sent
    When messages are read
    Then  all response messages have the label 'SENT'

  Scenario: A Respondent sends multiple messages, and Internal user reads them confirm all have INBOX and UNREAD  labels
    Given sending from respondent to internal
      And  '5' messages are sent
      And the user is set as internal
    When messages are read
    Then  all response messages have the label 'INBOX'
      And all response messages have the label 'UNREAD'

  Scenario: An internal user sends multiple messages, and a respondent user reads them confirm all have INBOX and UNREAD  labels
    Given sending from internal to respondent
      And  '5' messages are sent
      And the user is set as respondent
    When messages are read
    Then  all response messages have the label 'INBOX'
      And all response messages have the label 'UNREAD'

   Scenario: A Respondent sends multiple messages against two rus, Internal user reads them confirm correct count seen
    Given sending from respondent to internal
      And  '5' messages are sent
      And  ru set to alternate ru
      And  '3' messages are sent
    When the user is set as internal
     And ru set to default ru
     And messages are read using current 'ru_id'
    Then  '5' messages are returned

  Scenario: An internal user sends multiple messages against two rus, Respondent user reads them confirm correct count seen
    Given sending from internal to respondent
      And  '5' messages are sent
      And  ru set to alternate ru
      And  '3' messages are sent
    When the user is set as respondent
     And ru set to default ru
     And messages are read using current 'ru_id'
    Then  '5' messages are returned

   Scenario: A Respondent sends multiple messages against two surveys, Internal user reads them confirm correct count seen
    Given sending from respondent to internal
      And  '5' messages are sent
      And  survey is set to alternate survey
      And  '3' messages are sent
    When the user is set as internal
     And survey set to default survey
     And messages are read using current 'survey'
    Then  '5' messages are returned

  Scenario: An internal user sends multiple messages against two surveys, respondent reads them confirm correct count seen
    Given sending from internal to respondent
      And  '5' messages are sent
      And  survey is set to alternate survey
      And  '3' messages are sent
    When the user is set as respondent
     And survey set to default survey
     And messages are read using current 'survey'
    Then  '5' messages are returned

  Scenario: A respondent user sends multiple messages against two collection cases, Internal user  reads them confirm correct count seen
    Given sending from respondent to internal
      And  '5' messages are sent
      And  collection case is set to alternate collection case
      And  '3' messages are sent
    When the user is set as internal
     And collection case set to default collection case
     And messages are read using current 'collection_case'
    Then  '5' messages are returned


   Scenario: An internal user sends multiple messages against two collection cases, Respondent  reads them confirm correct count seen
    Given sending from internal to respondent
      And  '5' messages are sent
      And  collection case is set to alternate collection case
      And  '3' messages are sent
    When the user is set as respondent
     And collection case set to default collection case
     And messages are read using current 'collection_case'
    Then  '5' messages are returned

  Scenario: A respondent user sends multiple messages against two collection exercises, Internal user  reads them confirm correct count seen
    Given sending from respondent to internal
      And  '5' messages are sent
      And  collection exercise is set to alternate collection exercise
      And  '3' messages are sent
    When the user is set as internal
     And collection exercise set to default collection exercise
     And messages are read using current 'collection_exercise'
    Then  '5' messages are returned


   Scenario: An internal user sends multiple messages against two collection exercises, Respondent  reads them confirm correct count seen
    Given sending from internal to respondent
      And  '5' messages are sent
      And  collection exercise is set to alternate collection exercise
      And  '3' messages are sent
    When the user is set as respondent
     And collection exercise set to default collection exercise
     And messages are read using current 'collection_exercise'
    Then  '5' messages are returned


   Scenario: A respondent sends multiple messages , An internal user reads one and then gets all UNREAD
     Given sending from respondent to internal
      And  '5' messages are sent
      And  the user is set as internal
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
     When  messages with a label of  'UNREAD' are read
     Then   '4' messages are returned
      And all response messages have the label 'INBOX'
      And all response messages have the label 'UNREAD'

   Scenario: An internal user sends multiple messages , A respondent user reads one and then gets all UNREAD
     Given sending from internal to respondent
      And  '5' messages are sent
      And  the user is set as respondent
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
     When  messages with a label of  'UNREAD' are read
     Then   '4' messages are returned
      And all response messages have the label 'INBOX'
      And all response messages have the label 'UNREAD'

   Scenario: A respondent sends multiple messages , An internal user reads one and then gets all marked as INBOX
     Given sending from respondent to internal
      And  '5' messages are sent
      And  the user is set as internal
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
     When  messages with a label of  'INBOX' are read
     Then   '5' messages are returned


   Scenario: An internal user sends multiple messages , A respondent user reads one and then gets all marked as INBOX
     Given sending from internal to respondent
      And  '5' messages are sent
      And  the user is set as respondent
      And  the message is read
      And  a label of 'UNREAD' is to be removed
      And  the message labels are modified
     When  messages with a label of  'INBOX' are read
     Then   '5' messages are returned


  Scenario: A respondent sends multiple messages , Another respondent should not be able to read any
     Given sending from respondent to internal
      And  '5' messages are sent
      And  the user is set as alternative respondent
     When messages are read
     Then  a success status code (200) is returned
      And '0' messages are returned

  Scenario: An internal user sends multiple messages , Another respondent should not be able to read any
     Given sending from internal to respondent
      And  '5' messages are sent
      And  the user is set as alternative respondent
     When messages are read
     Then  a success status code (200) is returned
      And '0' messages are returned

  Scenario: A respondent sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given sending from respondent to internal
      And  '23' messages are sent
     When messages are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: An internal user sends multiple messages then sets the limit to a smaller number and reads messages , assert correct number returned
     Given sending from respondent to internal
      And  '23' messages are sent
     When messages are read with '5' per page requesting page '5'
     Then  a success status code (200) is returned
      And '3' messages are returned

  Scenario: An internal user sends multiple messages , all should be returned with sent from internal True
    Given sending from internal to respondent
      And '7' messages are sent
    When messages with a label of  'SENT' are read
      Then a success status code (200) is returned
      And '7' messages are returned with sent from internal

  Scenario: An external user sends multiple messages , no messages should be returned with sent from internal true
    Given sending from respondent to internal
      And '7' messages are sent
    When messages are read
      Then a success status code (200) is returned
      And '0' messages are returned with sent from internal