Feature: V2 access with existing V1 Data

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario Outline: There are existing messages to internal user , A respondent adds more using V2 , all should be returned on get messages
    Given sending from respondent to internal user
      And the message is sent
      And the message is sent
      And the message is sent
      And sending from respondent to internal <user>
      And the message is sent V2
      And the message is sent V2
   When messages are read V2
    Then  a success status code (200) is returned
      And '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

Scenario Outline: There are existing messages from BRES , an internal user adds more , the respondent should see all of them
    Given sending from internal user to respondent
      And the message is sent
      And the message is sent
      And the message is sent
      And sending from internal <user> to respondent
      And the message is sent V2
      And the message is sent V2
   When the user is set as respondent
      And messages are read V2
    Then  a success status code (200) is returned
      And '5' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

