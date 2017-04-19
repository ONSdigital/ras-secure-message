Feature: Checking request is valid

  Scenario: GET request without a user urn in header
    Given no user urn is in the header
    When a GET request is made
    Then a 400 HTTP response is returned

  Scenario: POST request without a user urn in header
    Given no user urn is in the header
    When a POST request is made
    Then a 400 HTTP response is returned
