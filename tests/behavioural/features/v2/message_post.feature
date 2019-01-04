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