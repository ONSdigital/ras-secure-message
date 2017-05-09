Feature: Draft Put Endpoint

  Scenario: An existing draft is updated 200 is returned
    Given a valid draft has been modified
    When it is saved
    Then a 200 is returned

  Scenario: A new draft is updated
    Given a non-existing draft is modified
    When it is saved
    Then a 400 error status is returned