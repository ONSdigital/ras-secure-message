Feature: Message Send V2 Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent sending a valid message to specific user and receiving a 201
    Given sending from respondent to internal <user>
    When the message is sent V2
    Then a created status code 201 is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: Internal user  sending a valid message to respondent user and receiving a 201
    Given sending from internal <user> to respondent
    When the message is sent V2
    Then a created status code 201 is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario:Respondent tries to retrieve a conversation that they are not part of via thread id
    Given sending from respondent to internal specific user
      And   the message is sent
      And   the thread id is set to the last returned thread id
    When the user is set as alternative respondent
     And  the thread is read
    Then a not found status code 404 is returned
