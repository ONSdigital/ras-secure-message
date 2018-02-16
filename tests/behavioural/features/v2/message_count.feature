Feature: Unread Message count endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending multiple valid messages to non bres user , non bres user should have same number of unread messages
    Given sending from respondent to internal <user>
      And the survey is set to 'SomeSurvey'
    When '5' messages are sent using V2
      And the user is set as internal <user>
      And the count of  messages with 'UNREAD' label in survey 'SomeSurvey' is made V2
    Then the returned label count was '5' V2

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: Internal user  sending multiple valid messages  , respondent should have same number of unread messages
    Given sending from internal <user> to respondent
      And the survey is set to 'SomeSurvey'
    When '5' messages are sent using V2
      And the user is set as respondent
      And the count of  messages with 'UNREAD' label in survey 'SomeSurvey' is made V2
    Then the returned label count was '5' V2

    Examples: user type
    | user        |
    | specific user |
    | group        |