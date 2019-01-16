Feature: Threads count endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending multiple valid messages to group , non specific user should have same number of threads
    Given sending from respondent to internal group
      And the survey is set to 'SomeSurvey'
    When '5' messages are sent using V2
      And the user is set as internal <user>
      And the count of open threads in survey 'SomeSurvey' is made V2
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
When the count of open threads in survey 'SomeSurvey' is made V2
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
When the count of open threads in survey 'Survey2' is made V2
Then the thread count is '4' threads

Examples: user type
| user        |
| specific user |
| group        |


Scenario: Respondent sends multiple messages to an internal user, that internal user gets the threads count for their conversations
  Given sending from respondent to internal specific user
   And '7' messages are sent
  When the user is set as internal specific user
   And the count of open threads for current user is made
  Then the thread count is '7' threads


Scenario: Respondent sends multiple messages to an internal user, a different internal user gets the threads count for their
  Given sending from respondent to internal specific user
   And '7' messages are sent
  When the user is set to alternative internal specific user
   And the count of open threads for current user is made
  Then the thread count is '0' threads


Scenario: Internal user gets threads count with both is_closed and my_conversations set
 Given sending from respondent to internal specific user
   And '7' messages are sent
  When the user is set to alternative internal specific user
   And the count of closed threads for current user is made
  Then the thread count is '0' threads


Scenario: respondent gets threads count
  Given sending from respondent to internal specific user
   And '7' messages are sent
  When the count of open threads for current user is made
  Then a forbidden status code 403 is returned


Scenario: two internal users send to a respondent
  Given sending from internal specific user to respondent
   And '7' messages are sent
   And sending from alternate internal specific user to respondent
   And '9' messages are sent
  When the user is set as internal specific user
   And the count of open threads for current user is made
  Then the thread count is '7' threads

Scenario: Respondent sends multiple messages to group , internal user gets count
   Given sending from respondent to internal group
   And '7' messages are sent
  When the user is set as internal specific user
   And the count of open threads for current user is made
  Then the thread count is '0' threads


Scenario: Respondent sends messages to different ce, internal user filters by ce
  Given sending from respondent to internal specific user
    And the collection_exercise is set to 'ce1'
    And the message is sent V2
    And the collection_exercise is set to 'ce1'
    And the message is sent V2
    And the collection_exercise is set to 'ce2'
    And the message is sent V2
  When  the user is set as internal specific user
    And the count of open threads for current user and ce of 'ce1' is made
  Then  the thread count is '2' threads


Scenario: Respondent sends messages to different cc, internal user filters by cc
  Given sending from respondent to internal specific user
    And the collection case is set to 'cc1'
    And the message is sent V2
    And the collection case is set to 'cc1'
    And the message is sent V2
    And the collection case is set to 'cc2'
    And the message is sent V2
  When  the user is set as internal specific user
    And the count of open threads for current user and cc of 'cc1' is made
  Then  the thread count is '2' threads


Scenario: Respondent sends messages to different ru, internal user filters by ru
  Given sending from respondent to internal specific user
    And the ru is set to 'ru1'
    And the message is sent V2
    And the ru is set to 'ru1'
    And the message is sent V2
    And the ru is set to 'ru2'
    And the message is sent V2
  When  the user is set as internal specific user
    And the count of open threads for current user and ru of 'ru1' is made
  Then  the thread count is '2' threads
