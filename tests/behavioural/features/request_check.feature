Feature: Checking all request pass authorisation
   """ requests to any endpoint all hit the same authorisation point before being passed to the specific endpoint """

  Scenario: GET request without a user urn in header
    Given no user urn is in the header
    When a GET request is made
    Then a 400 error status is returned

  Scenario: POST request without a user urn in header
    Given no user urn is in the header
    When a POST request is made
    Then a 400 error status is returned

  @ignore
  Scenario: PUT request without a user urn in header
    Given no user urn is in the header
    When a PUT request is made
    Then a 400 error status is returned

  @ignore
  Scenario Outline: User tries to use endpoint with the wrong method
    Given user wants to use a particular endpoint <endpoint>
    When user tries to access that endpoint with the wrong method <wrong method>
    Then a 405 error status is returned

  Examples: endpoint wrong methods
    |       endpoint        |   wrong method    |
    |       /draft/save     |       GET         |
    |       /draft/save     |       PUT         |
    |       /healthRest     |       POST        |
    |       /healthRest     |       PUT         |
    |       /health/db      |       POST        |
    |       /health/db      |       PUT         |
    |    /health/details    |       PUT         |
    |    /health/details    |       POST        |
    | /message/<message_id> |       POST        |
    | /message/<message_id> |       PUT         |
    |/message/<message_id>/modify|  GET         |
    |/message/<message_id>/modify|  POST        |
    |     /message/send     |       PUT         |
    |     /message/send     |       GET         |
    |       /messages       |       PUT         |
    |       /messages       |       POST        |
