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


 Scenario Outline: An internal user sends a very long message, the respondent sees a 100 character summary in their inbox
    Given sending from internal <user> to respondent
      And the message body is '5000' characters long
      And '1' messages are sent using V2
    When messages are read V2
    Then the message bodies are '100' characters or less

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

  Scenario: Respondent saves a message to GROUP and gets message list verify the @msg_to is correctly populated
    Given sending from respondent to internal group
      And   the message is sent V2
      And messages are read V2
    Then a success status code (200) is returned
      And the at_msg_to is set correctly for internal group for all messages

  Scenario: Respondent saves a message to BRES using V1 and gets message list using V2 verify the @msg_to is correctly populated
    Given sending from respondent to internal group
      And   the message is sent
      And messages are read V2
    Then a success status code (200) is returned
      And the at_msg_to is set correctly for bres user for all messages

  Scenario: There are 50 messages between respondent and internal user. Internal user gets conversations should see 50
   Given sending from respondent to internal group
    And '50' messages are sent using V2
   When the user is set as internal specific user
    And messages are read V2
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 messages between internal user and respondent. Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent using V2
   When the user is set as respondent
    And messages are read V2
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 messages between internal user and respondent. Alternative Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent using V2
   When the user is set to alternative internal specific user
    And messages are read V2
   Then  '50' messages have a 'SENT' label
