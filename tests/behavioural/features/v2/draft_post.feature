Feature: Draft Save Endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent saves a draft and receives a 201
    Given sending from respondent to internal <user>
    When the message is saved as draft V2
    Then a created status code 201 is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: An internal user saves a draft and receives a 201
    Given sending from internal <user> to respondent
    When the message is saved as draft V2
    Then a created status code 201 is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |