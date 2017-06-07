Feature: Get threads list Endpoint

  Scenario: Respondent and internal user have multiple conversations and respondent retrieves all conversation
    Given a respondent and internal user have multiple conversations
    When the respondent gets all conversations
    Then most recent message from each conversation is returned

  Scenario: Respondent and internal user have multiple conversations and internal user retrieves all conversation
    Given a respondent and internal user have multiple conversations
    When the internal user gets all conversations
    Then most recent message from each conversation is returned

  Scenario: Respondent and internal user have multiple conversations, including a draft, and respondent retrieves all conversation
    Given a respondent and internal user have multiple conversations
    And internal user has conversation with a draft
    When the respondent gets all conversations
    Then most recent message from each conversation is returned

  Scenario: Respondent and internal user have multiple conversations, including a draft, and internal user retrieves all conversation
    Given a respondent and internal user have multiple conversations
    And internal user has conversation with a draft
    When the internal user gets all conversations
    Then most recent message from each conversation is returned including draft