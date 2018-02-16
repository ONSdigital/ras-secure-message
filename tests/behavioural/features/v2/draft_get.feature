Feature: Get draft by id V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: A Respondent saves a draft and reads it
      And sending from respondent to internal <user>
      And  the message is saved as draft V2
    When the draft is read V2
    Then a success status code (200) is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: An internal user saves a draft and reads it
    Given sending from internal <user> to respondent
      And  the message is saved as draft V2
    When the draft is read V2
    Then a success status code (200) is returned

    Examples: user type
    | user        |
    | specific user |
    | group        |
