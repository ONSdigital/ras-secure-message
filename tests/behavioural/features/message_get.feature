Feature: Message get by ID Endpoint

  Scenario: Retrieve a message with correct missing ID
    Given there is a message to be retrieved
    When the get request is made with a correct message id
    Then a 200 HTTP response is returned

  Scenario: Retrieve a message with incorrect missing ID
    Given there is a message to be retrieved
    When the get request has been made with an incorrect message id
    Then a 404 HTTP response is returned
