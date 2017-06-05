Feature: Get thread by id Endpoint

  Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation
    Given a respondent and internal user have a conversation
    When the respondent gets this conversation
    Then all messages from that conversation should be received

  Scenario: Respondent and internal user have a conversation and internal user retrieves the conversation
    Given a respondent and internal user have a conversation
    When the internal user gets this conversation
    Then all messages from that conversation should be received
