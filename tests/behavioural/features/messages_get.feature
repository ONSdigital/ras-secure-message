Feature: Get Messages list Endpoint

  Background: Reset database
    Given database is reset

  Scenario: Respondent sends multiple messages and retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the respondent gets their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Internal user sends multiple messages and retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Internal user gets their messages
    Then the retrieved messages should have the correct SENT labels

  Scenario: Respondent sends multiple messages and internal user retrieves the list of messages with their labels
    Given a respondent sends multiple messages
    When the Internal user gets their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels
    Given a Internal user sends multiple messages
    When the Respondent gets their messages
    Then the retrieved messages should have the correct INBOX and UNREAD labels

 Scenario: As an external user I would like to be able to view a list of messages
    Given an external user has multiple messages
    When the external user requests all messages
    Then all of that users messages are returned

 Scenario: As an internal user I would like to be able to view a list of messages
    Given an internal user has multiple messages
    When the internal user requests all messages
    Then all of that users messages are returned

  Scenario: Respondent and internal user sends multiple messages and Respondent retrieves the list of sent messages 
    Given a respondent and an Internal user sends multiple messages 
    When the Respondent gets their sent messages 
    Then the retrieved messages should all have sent labels

  Scenario Outline: As a user I would like to be able to view a list of inbox messages
    Given a <User> user receives multiple messages 
    When the <User> user gets their inbox messages 
    Then the retrieved messages should all have inbox labels

    Examples: Users
    |User       |
    |internal   |
    |respondent |


  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular reporting unit
    Given a Internal user sends multiple messages with different reporting unit 
    When the Respondent gets their messages with particular reporting unit 
    Then the retrieved messages should have the correct reporting unit

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular survey 
    Given a Internal user sends multiple messages with different survey 
    When the Respondent gets their messages with particular survey 
    Then the retrieved messages should have the correct survey

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular collection case 
    Given a Internal user sends multiple messages with different collection case 
    When the Respondent gets their messages with particular collection case 
    Then the retrieved messages should have the correct collection case

  Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular collection exercise 
    Given a Internal user sends multiple messages with different collection exercise 
    When the Respondent gets their messages with particular collection exercise 
    Then the retrieved messages should have the correct collection exercise

  Scenario: Respondent creates multiple draft messages and Respondent retrieves the list of draft messages 
    Given a Respondent creates multiple draft messages 
    When the Respondent gets their draft messages 
    Then the retrieved messages should all have draft labels

  Scenario: Respondent creates multiple draft messages and Internal user retrieves a list of messages 
    Given a Respondent creates multiple draft messages 
    When the Internal user gets their messages
    Then the retrieved messages should not have DRAFT_INBOX labels

  @ignore
  Scenario Outline: User provides parameters that are invalid
    Given parameter <param> has value <value>
    When user gets messages using the parameters
    Then a 400 HTTP bad syntax response is returned

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
    Then a 400 HTTP bad syntax response is returned

  Examples: Parameters
    |param         | value |
    |reportingUnit | LongerThan11Chars |
    |labels        | INBOX-SENT-ARCHIVED-DRAFT-INBOX-SENT-ARCHIVED-DRAFT |

  @ignore
  Scenario Outline: User gets messages with various labels options
    Given there are multiple messages to retrieve for all labels
    When respondent gets messages with labels <labels>
    Then messages returned should have one of the labels <labels>

  Examples: Parameters
    |labels  |
    |INBOX   |
    |SENT    |
    |ARCHIVED |
    |DRAFT   |
    |INBOX-SENT  |
    |INBOX-SENT-ARCHIVED |
    |INBOX-SENT-ARCHIVED-DRAFT |

  @ignore
  Scenario: User gets messages with no labels options
    Given there are multiple messages to retrieve for all labels
    When respondent gets messages with labels empty
    Then all messages should be returned

