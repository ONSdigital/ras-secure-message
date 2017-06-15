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
    Then a 404 HTTP response is returned