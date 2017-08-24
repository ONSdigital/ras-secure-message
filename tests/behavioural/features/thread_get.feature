Feature: Get thread by id Endpoint

  Background: Reset database
    Given database is reset

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation
    Given a respondent and internal user have a conversation
    When the respondent gets this conversation
    Then all messages from that conversation should be received

  Scenario: Respondent and internal user have a conversation and internal user retrieves the conversation
    Given a respondent and internal user have a conversation
    When the internal user gets this conversation
    Then all messages from that conversation should be received

  Scenario: Respondent and internal user have a conversation, including a draft, and respondent retrieves the conversation
    Given a respondent and internal user have a conversation
    And internal user creates a draft
    When the respondent gets this conversation
    Then all messages from that conversation should be received

  Scenario: Respondent and internal user have a conversation, including a draft, and internal user retrieves the conversation
    Given a respondent and internal user have a conversation
    And internal user creates a draft
    When the internal user gets this conversation
    Then all messages from that conversation should be received including draft

  Scenario: Respondent and internal user have a conversation and internal user retrieves that conversation from multiple conversations
    Given a respondent and internal user have a conversation
    And internal user has multiple conversations
    When the internal user gets this conversation
    Then all messages from that conversation should be received

  Scenario: User tries to retrieve a conversation that does not exist
    Given a respondent picks a conversation that does not exist
    When the respondent gets this conversation
    Then a not found status code (404) is returned

  @ignore
  Scenario: Messages saved with survey id should  not be retrieved by setting actor equal to survey id
    Given a message is sent to an internal user
    When the internal user requests thread with actor equal to survey
    Then none should be returned

  @ignore
  Scenario: Messages saved with survey id should be retrieved by setting survey equal to survey id
    Given a message is sent to an internal user
    When the internal user requests thread with survey equal to survey_id
    Then one should be returned