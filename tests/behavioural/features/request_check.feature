Feature: Checking all request pass authorisation
   """ requests to any endpoint all hit the same authorisation point before being passed to the specific endpoint """

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: A Respondent requests a message without a user being defined
    Given new sending from respondent to internal
      And  new the message is sent
    When  the user token is set to respondent with no user id
      And new the message is read
    Then a bad request status code (400) is returned

  Scenario: An internal user requests a message without a user being defined
    Given new sending from internal to respondent
      And  new the message is sent
    When  the user token is set to internal with no user id
      And new the message is read
    Then a bad request status code (400) is returned

  Scenario: A Respondent posts a message without a user being defined
    Given new sending from respondent to internal
       And  the user token is set to respondent with no user id
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: An internal user posts a message without a user being defined
    Given new sending from internal to respondent
      And the user token is set to internal with no user id
    When  new the message is sent
    Then a bad request status code (400) is returned

  Scenario: A Respondent modifies a message without a user being defined
    Given new sending from respondent to internal
      And the user token is set to respondent with no user id
      And new the message is sent
    When new the message labels are modified
    Then a bad request status code (400) is returned

  Scenario: An internal user modifies a message without a user being defined
    Given new sending from internal to respondent
      And the user token is set to internal with no user id
      And new the message is sent
    When new the message labels are modified
    Then a bad request status code (400) is returned

  Scenario: A respondent requests a message without a role being defined
    Given new sending from respondent to internal
      And new the message is sent
    When the user token is set to a respondent with no role associated
      And new the message is read
    Then a bad request status code (400) is returned

  Scenario: An internal user requests a message without a role being defined
    Given new sending from internal to respondent
      And new the message is sent
    When the user token is set to a internal user with no role associated
      And new the message is read
    Then a bad request status code (400) is returned

  Scenario: A Respondent modifies a message without a role being defined
    Given new sending from respondent to internal
      When the user token is set to a respondent with no role associated
      And new the message is sent
    When new the message labels are modified
    Then a bad request status code (400) is returned

  Scenario: An internal user modifies a message without a role being defined
    Given new sending from internal to respondent
      When the user token is set to a internal user with no role associated
      And new the message is sent
    When new the message labels are modified
    Then a bad request status code (400) is returned

  Scenario Outline: Internal user tries to use endpoint with the wrong method
    Given new sending from internal to respondent
    When new user accesses the <endpoint> endpoint with using the <wrong method> method
    And a debug step
    Then a not allowed status code (405) is returned

    Examples: endpoint wrong methods
    |       endpoint        |   wrong method    |
    |       /draft/save     |       PUT         |
    |       /health         |       POST        |
    |       /health         |       PUT         |
    |       /health/db      |       POST        |
    |       /health/db      |       PUT         |
    |    /health/details    |       PUT         |
    |    /health/details    |       POST        |
    |       /message/id     |       POST        |
    |       /message/id     |       PUT         |
    |   /message/id/modify  |       GET         |
    |   /message/id/modify  |       POST        |
    |     /message/send     |       PUT         |
    |       /messages       |       PUT         |
    |       /messages       |       POST        |


