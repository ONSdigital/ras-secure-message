Feature: Threads count endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending multiple valid messages to internal , internal user should have same number of threads
    Given sending from respondent to internal group
      And survey set to default survey
    When '5' messages are sent
      And the user is set as internal <user>
      And the count of open threads in default survey is made
    Then the returned label count was '5'

    Examples: user type
    | user        |
    | specific user |
    | group        |


Scenario Outline: Respondent sends multiple messages to internal , some to group/user,  internal reads unread messages , validate threads count
Given sending from respondent to internal group
  And survey set to default survey
  And '5' messages are sent
  And sending from respondent to internal <user>
  And '4' messages are sent
  And the user is set as internal <user>
  And the count of open threads in default survey is made
Then the returned label count was '9'

Examples: user type
| user        |
| specific user |
| group        |


Scenario Outline: Respondent sends multiple messages to internal on different surveys internal reads inbox messages , count should be correct for each survey
Given sending from respondent to internal <user>
  And the survey is set to 'additional_survey_1'
  And '5' messages are sent
  And the survey is set to 'additional_survey_2'
  And '4' messages are sent
  And the survey is set to 'additional_survey_3'
  And '3' messages are sent
  And the user is set as internal <user>
When the count of open threads in survey 'additional_survey_2'
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

Scenario: Respondent starts 4 conversations Internal user gets threads count with new_respondent_conversations set
   Given sending from respondent to internal group
   And '4' messages are sent
  When the user is set to alternative internal specific user
   And the count of threads for new respondent conversations is made
  Then the thread count is '4' threads

Scenario: Respondent 2 conversations each with 2 messages, Internal user gets threads count with new_respondent_conversations set
   Given sending from respondent to internal group
   And the message is sent
   And the thread id is set to the last returned thread id
   And the message is sent
   And the thread_id is set to empty
   And the message is sent
   And the thread id is set to the last returned thread id
   And the message is sent
  When the user is set to alternative internal specific user
   And the count of threads for new respondent conversations is made
  Then the thread count is '2' threads

Scenario: 2 Respondents start conversations , Internal user gets threads count with new_respondent_conversations set
   Given sending from respondent to internal group
   And the message is sent
   And the message is sent
   And the user is set as alternative respondent
   And the message is sent
   And the message is sent
  When the user is set to alternative internal specific user
   And the count of threads for new respondent conversations is made
  Then the thread count is '2' threads

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
    And the message is sent
    And the collection_exercise is set to 'ce1'
    And the message is sent
    And the collection_exercise is set to 'ce2'
    And the message is sent
  When  the user is set as internal specific user
    And the count of open threads for current user and ce of 'ce1' is made
  Then  the thread count is '2' threads


Scenario: Respondent sends messages to different cc, internal user filters by cc
  Given sending from respondent to internal specific user
    And the collection case is set to 'cc1'
    And the message is sent
    And the collection case is set to 'cc1'
    And the message is sent
    And the collection case is set to 'cc2'
    And the message is sent
  When  the user is set as internal specific user
    And the count of open threads for current user and cc of 'cc1' is made
  Then  the thread count is '2' threads


Scenario: Respondent sends messages to different ru, internal user filters by ru
  Given sending from respondent to internal specific user
    And the business_id is set to 'additional_ru1'
    And the message is sent
    And the business_id is set to 'additional_ru1'
    And the message is sent
    And the business_id is set to 'additional_ru2'
    And the message is sent
  When  the user is set as internal specific user
    And the count of open threads for current user and business_id of 'additional_ru1' is made
  Then  the thread count is '2' threads

Scenario: Internal user gets threads count with all_conversation_types when messages sent to a specific user
   Given sending from respondent to internal specific user
     And '7' messages are sent
    When the user is set as internal specific user
     And the count of all conversation types closed threads for current user is made
    Then the thread open count is '7' threads
     And the thread closed count is '0' threads
     And the thread my_conversations count is '7' threads
     And the thread new_respondent_conversations count is '0' threads

Scenario: Internal user gets threads count with all_conversation_types when messages sent to a general user
   Given sending from respondent to internal group
     And '7' messages are sent
    When the user is set as internal specific user
     And the count of all conversation types closed threads for current user is made
    Then the thread open count is '7' threads
     And the thread closed count is '0' threads
     And the thread my_conversations count is '0' threads
     And the thread new_respondent_conversations count is '7' threads

Scenario: Internal user gets threads count with all_conversation_types with a closed message and messages sent to GROUP
   Given sending from respondent to internal group
     And '7' messages are sent
     And the user is set as internal specific user
     And the last returned thread is closed
    When the count of all conversation types closed threads for current user is made
    Then the thread open count is '6' threads
     And the thread closed count is '1' threads
     And the thread my_conversations count is '0' threads
     And the thread new_respondent_conversations count is '6' threads