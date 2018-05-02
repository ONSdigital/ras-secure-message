Feature: Get info

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: User requests draft
    Given the user requests endpoint info
    Then  the endpoint info is returned
    And   a success status code 200 is returned


