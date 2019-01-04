Feature: Threads count endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending multiple valid messages to group , non specific user should have same number of threads
    Given sending from respondent to internal group
      And the survey is set to 'SomeSurvey'
    When '5' messages are sent using V2
      And the user is set as internal <user>
      And the count of open threads in survey'SomeSurvey' is made V2
    Then the returned label count was '5' V2

    Examples: user type
    | user        |
    | specific user |
    | group        |


Scenario Outline: Respondent sends multiple messages to internal , some to group/user,  internal reads unread messages , validate threads count
Given sending from respondent to internal group
  And the survey is set to 'SomeSurvey'
  And '5' messages are sent
  And sending from respondent to internal <user>
  And '4' messages are sent using V2
  And the user is set as internal <user>
When the count of open threads in survey'SomeSurvey' is made V2
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
When the count of open threads in survey'Survey2' is made V2
Then the returned label count was '4' V2

Examples: user type
| user        |
| specific user |
| group        |

Scenario: Respondent sends multiple messages to an internal user, that internal user gets the threads count
  Given sending from respondent to internal specific user
   And '7' messages are sent
  When the user is set as internal specific user
   And the count of open threads is made
  Then '7' messages are returned


Scenario: Respondent sends multiple messages to an internal user, a different internal user gets the threads count

Scenario: Internal user gets threads count with both is_closed and my_conversations set

Scenario: respondent gets threads count

Scenario: Respondent sends multiple messages to two internal respondents

Scenario: Respondent sends multiple messages to group , internal user gets count