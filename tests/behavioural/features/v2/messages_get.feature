Feature: Get Messages list V2 Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: A Respondent sends multiple messages using v2 , Internal user reads them confirm correct count seen
    Given sending from respondent to internal <user>
      And  '5' messages are sent using V2
    When messages are read V2
    Then  '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: An internal user sends multiple messages, Internal user reads them confirm correct count seen
    Given sending from internal <user> to respondent
      And  '5' messages are sent using V2
    When messages with a label of  'SENT' are read
    Then  '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: An internal user sends multiple messages against two rus, Respondent user reads them confirm correct count seen
    Given sending from internal <user> to respondent
      And  '5' messages are sent using V2
      And  ru set to alternate ru
      And  '3' messages are sent using V2
    When the user is set as respondent
     And ru set to default ru
     And messages are read using current 'ru_id'
    Then  '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


 Scenario Outline: An internal user sends multiple messages to two respondents , then one respondent is forgotten by party service , all messages should be retrieved on get messages
    Given sending from internal <user> to respondent
      And  '5' messages are sent using V2
      And  the to is set to alternative respondent
      And  '3' messages are sent using V2
      And  party service forgets alternative respondent
    When messages are read V2
    Then  '8' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: A Respondent sends multiple messages using v2 on different surveys to multiple internal user types ,
                    Internal user reads them without setting a survey confirm correct count seen
    Given sending from respondent to internal <user>
      And the survey is set to 'Survey1'
      And  '5' messages are sent using V2
      And sending from respondent to internal bres user
      And the survey is set to 'Survey2'
    And  '7' messages are sent using V2
    When  messages are read V2
    Then  '12' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: A Respondent sends multiple messages using v2 on different surveys to multiple internal user types ,
                    Internal user reads them for a survey confirm correct count seen
    Given sending from respondent to internal <user>
      And the survey is set to 'Survey1'
      And  '5' messages are sent using V2
      And sending from respondent to internal bres user
      And the survey is set to 'Survey2'
    And  '7' messages are sent using V2
    When  messages are read using survey of 'Survey1'
    Then  '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |