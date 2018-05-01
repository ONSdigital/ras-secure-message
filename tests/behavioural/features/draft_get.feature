Feature: Get draft by id

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: A Respondent saves a draft and reads it
    Given sending from respondent to internal specific user
    And the message is saved as draft
    When the draft is read
    Then a success status code 200 is returned

  Scenario: An internal user saves a draft and reads it
    Given sending from internal specific user to respondent
      And  the message is saved as draft
    When the draft is read
    Then a success status code 200 is returned

  Scenario: A Respondent attempts to read a draft that does not exist
    Given sending from respondent to internal specific user
      And the msg_id is set to '1234'
    When the draft is read
    Then a not found status code 404 is returned

  Scenario: An internal user attempts to read a draft that does not exist
    Given sending from internal specific user to respondent
      And the msg_id is set to '1234'
    When the draft is read
    Then a not found status code 404 is returned

  Scenario: Respondent requests draft not authorised to view
    Given sending from internal specific user to respondent
      And   the message is saved as draft
      And   the user is set as alternative respondent
    When  the draft is read
    Then  a forbidden status code 403 is returned

   Scenario: An internal user requests draft not authorised to view
    Given sending from respondent to internal specific user
      And   the message is saved as draft
      And   the user is set as alternative respondent
    When  the draft is read
    Then  a forbidden status code 403 is returned

  Scenario: A Respondent saves a draft and reads it with etag header
    Given sending from respondent to internal specific user
      And  the message is saved as draft
    When an etag is requested
      And the draft is read
    Then a success status code 200 is returned
      And the response should include a valid etag

  Scenario: An internal user saves a draft and reads it with etag header
    Given sending from internal specific user to respondent
      And  the message is saved as draft
    When an etag is requested
      And the draft is read
    Then a success status code 200 is returned
      And the response should include a valid etag

  Scenario: An internal user saves a draft and the respondent is not authorized to read it
    Given sending from internal specific user to respondent
      And  the message is saved as draft
      And  the user is set as respondent
      And  the draft is read
    Then  a forbidden status code 403 is returned

  Scenario: Respondent saves a draft with an empty to field then reads it , should receive a 200
    Given sending from respondent to internal specific user
      And  the to is set to empty
    When the message is saved as draft
      And the draft is read
    Then a success status code 200 is returned

  Scenario: Internal user saves a draft with an empty to field then reads it , should receive a 200
    Given sending from internal specific user to respondent
      And  the to is set to empty
    When the message is saved as draft
      And the draft is read
    Then a success status code 200 is returned

