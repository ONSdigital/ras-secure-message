Feature: Checking all request pass authorisation
   """ requests to any endpoint all hit the same authorisation point before being passed to the specific endpoint """

  Background: Reset database
    Given database is reset
    And using mock party service
    And using mock case service

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

  @ignore
  Scenario: POST request without a user in header
    Given no user uuid is in the header
    When a POST request is made
    Then a bad request status code (400) is returned

  Scenario: PUT request without a user in header
    Given no user uuid is in the header
    When a PUT request is made
    Then a bad request status code (400) is returned

  Scenario: GET request without a role in header
    Given no role is in the header
    When a GET request is made
    Then a bad request status code (400) is returned

  Scenario: POST request without a role in header
    Given no role is in the header
    When a POST request is made
    Then a bad request status code (400) is returned

  Scenario: PUT request without a role in header
    Given no role is in the header
    When a PUT request is made
    Then a bad request status code (400) is returned

  Scenario Outline: User tries to use endpoint with the wrong method
    Given user wants to use <endpoint> endpoint
    When user tries to access that endpoint with the <wrong method> method
    Then a '405' status code is returned

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
