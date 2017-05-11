Feature: Get Messages list Endpoint

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

  @ignore
 Scenario: As an external user I would like to be able to view a list of messages
    Given multiple messages have been sent to an external user
    When the external user navigates to their messages
    Then messages are displayed

  Scenario: Respondent and internal user sends multiple messages and Respondent retrieves the list of sent messages 
    Given a respondent and an Internal user sends multiple messages 
    When the Respondent gets their sent messages 
    Then the retrieved messages should all have sent labels

  Scenario: Respondent and internal user sends multiple messages and Respondent retrieves the list of inbox messages 
    Given a respondent and an Internal user sends multiple messages 
    When the Respondent gets their inbox messages 
    Then the retrieved messages should all have inbox labels

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

  Scenario: Respondent creates multiple draft messages and Respondent retrieves the list of draft messages 
    Given a Respondent creates multiple draft messages 
    When the Respondent gets their draft messages 
    Then the retrieved messages should all have draft labels

  Scenario: Respondent creates multiple draft messages and Internal user retrieves a list of messages 
    Given a Respondent creates multiple draft messages 
    When the Internal user gets their messages
    Then the retrieved messages should not have DRAFT_INBOX labels

  @ignore
  Scenario Outline: User provides parameters that are too large or invalid
    Given parameter <param> has value <value>
    When user gets messages using the parameters
    Then a 400 HTTP bad syntax response is returned

  Examples: Parameters
    |param         | value |
    |limit         | string|
    |page          | string|
    |reportingUnit | LongerThan11Chars |
    |survey        | NotASurvey |
    |case          | ?|
    |labels        | NotALabel  |
    |labels        | INBOX-SENT-ARCHIVED-DRAFT-INBOX-SENT-ARCHIVED-DRAFT |

  @ignore
  Scenario Outline: User gets messages with various labels options
    Given there are multiple messages to retrieve for all labels
    When respondent gets messages with labels <labels>
    Then messages returned should have one of the labels <labels>

  Examples: Parameters
    |labels  |
    |empty   |
    |INBOX   |
    |SENT    |
    |ARCHIVED |
    |DRAFT   |
    |INBOX-SENT  |
    |INBOX-SENT-ARCHIVED |
    |INBOX-SENT-ARCHIVED-DRAFT |

