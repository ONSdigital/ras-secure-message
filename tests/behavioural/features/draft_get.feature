Feature: Get draft by id

  Background: Reset database
    Given database is reset
    And using mock party service
    And using mock case service

  Scenario: A Respondent saves a draft and reads it
    Given new sending from respondent to internal
      And  new the message is saved as draft
    When new the draft is read
    Then a success status code (200) is returned

  Scenario: An internal user saves a draft and reads it
    Given new sending from internal to respondent
      And  new the message is saved as draft
    When new the draft is read
    Then a success status code (200) is returned

  Scenario: A Respondent attempts to read a draft that does not exist
    Given new sending from respondent to internal
      And new the msg_id is set to '1234'
    When new the draft is read
    Then a not found status code (404) is returned

  Scenario: An internal user attempts to read a draft that does not exist
    Given new sending from internal to respondent
      And new the msg_id is set to '1234'
    When new the draft is read
    Then a not found status code (404) is returned

  Scenario: Respondent requests draft not authorised to view
    Given new sending from internal to respondent
      And   new the message is saved as draft
      And   new the user is set as alternative respondent
    When  new the draft is read
    Then  a forbidden status code (403) is returned

   Scenario: An internal user requests draft not authorised to view
    Given new sending from respondent to internal
      And   new the message is saved as draft
      And   new the user is set as alternative respondent
    When  new the draft is read
    Then  a forbidden status code (403) is returned

  Scenario: A Respondent saves a draft and reads it with etag header
    Given new sending from respondent to internal
      And  new the message is saved as draft
    When new an etag is requested
      And new the draft is read
    Then a success status code (200) is returned
      And an etag should be sent with the draft

  Scenario: An internal user saves a draft and reads it with etag header
    Given new sending from internal to respondent
      And  new the message is saved as draft
    When new an etag is requested
      And new the draft is read
    Then a success status code (200) is returned
      And an etag should be sent with the draft

