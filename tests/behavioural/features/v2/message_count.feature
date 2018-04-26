Feature: Unread Message count endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending multiple valid messages internal user , internal user should have same number of unread messages
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



Scenario Outline: Respondent sends multiple messages to internal group/user reads unread messages , count should include all messages
Given sending from respondent to internal user
  And the survey is set to 'SomeSurvey'
  And '5' messages are sent
  And sending from respondent to internal <user>
  And '4' messages are sent using V2
  And the user is set as internal <user>
When the count of  messages with 'UNREAD' label in survey 'SomeSurvey' is made V2
Then the returned label count was '9' V2

Examples: user type
| user        |
| specific user |
| group        |


Scenario Outline: Respondent sends multiple messages to internal on different surveys internal reads inbox messages , count should be correct for each survey
Given sending from respondent to internal <user>
  And the survey is set to 'Survey1'
  And '5' messages are sent
  And the survey is set to 'Survey2'
  And '4' messages are sent using V2
  And the survey is set to 'Survey3'
  And '3' messages are sent using V2
  And the user is set as internal <user>
When the count of  messages with 'UNREAD' label in survey 'Survey2' is made V2
Then the returned label count was '4' V2

Examples: user type
| user        |
| specific user |
| group        |


Scenario Outline: Respondent sends multiple messages to internal on different surveys internal reads inbox messages
                  with no survey specified , count should be all messaegs
Given sending from respondent to internal <user>
  And the survey is set to 'Survey1'
  And '5' messages are sent
  And the survey is set to 'Survey2'
  And '4' messages are sent using V2
  And the survey is set to 'Survey3'
  And '3' messages are sent using V2
  And the user is set as internal <user>
When the count of messages with 'UNREAD' label is made V2
Then the returned label count was '12' V2

Examples: user type
| user        |
| specific user |
| group        |