Feature: Draft Save Endpoint

 Background: Reset database
    Given using mock party service
    And using mock case service
    And database is reset

  Scenario: Respondent saves a draft and receives a 201
    Given new sending from respondent to internal
    When new the message is saved as draft
    Then a created status code (201) is returned

  Scenario: An internal user saves a draft and receives a 201
    Given new sending from internal to respondent
    When new the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Respondent saves a draft and receives a valid etag in the response
    Given new sending from respondent to internal
    When new the message is saved as draft
    Then new the response should include a valid etag

  Scenario: An internal user saves a draft and receives a valid etag in the response
    Given new sending from internal to respondent
    When new the message is saved as draft
    Then new the response should include a valid etag

  Scenario: Respondent saves a draft with an empty body , should receive a 201
    Given new sending from respondent to internal
      And  new the body is set to empty
    When new the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Internal user saves a draft with an empty body , should receive a 201
    Given new sending from internal to respondent
      And  new the body is set to empty
    When new the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Respondent saves a draft with a msg_id , should receive a 400
    Given new sending from respondent to internal
      And  new the msg_id is set to '12345678'
    When new the message is saved as draft
    Then a bad request status code (400) is returned

   Scenario: Internal user saves a draft with a msg_id , should receive a 400
    Given new sending from internal to respondent
      And  new the msg_id is set to '12345678'
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with to too long should receive a 400
    Given new sending from respondent to internal
      And  new the to field is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with to too long should receive a 400
    Given new sending from internal to respondent
      And  new the to field is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an empty to field , should receive a 201
    Given new sending from respondent to internal
      And  new the to is set to empty
    When new the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Internal user saves a draft with an empty to field , should receive a 201
    Given new sending from internal to respondent
      And new the to is set to empty
    When new the message is saved as draft
    Then a created status code (201) is returned


  Scenario: Respondent saves a draft from too long should receive a 400
    Given new sending from respondent to internal
      And  new the from is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft from too long should receive a 400
    Given new sending from internal to respondent
      And  new the from is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft body too long should receive a 400
    Given new sending from respondent to internal
      And  new the body is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft body too long should receive a 400
    Given new sending from internal to respondent
      And  new the body is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft subject too long should receive a 400
    Given new sending from respondent to internal
      And  new the subject is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft subject too long should receive a 400
    Given new sending from internal to respondent
      And  new the subject is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with missing from field should receive a 400 error
    Given new the user is set as respondent
      And  new the from is set to empty
      And  new the to is set to internal
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with missing from field should receive a 400 error
    Given new the user is set as internal
      And  new the from is set to empty
      And  new the to is set to respondent
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an empty survey field and receive a 400 error
    Given new sending from respondent to internal
      And  new the survey is set to empty
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an empty survey field and receive a 400 error
    Given new sending from internal to respondent
      And  new the survey is set to empty
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an collection case field too large and receive a 400 error
    Given new sending from respondent to internal
      And  new the collection case is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an collection case field too large and receive a 400 error
    Given new sending from internal to respondent
      And  new the collection case is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned


  Scenario: Respondent saves a draft with an collection exercise field too large and receive a 400 error
    Given new sending from respondent to internal
      And  new the collection exercise is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an collection exercise field too large and receive a 400 error
    Given new sending from internal to respondent
      And  new the collection exercise is too long
    When new the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft  when it is retrieved it should have a thread id equal to the msg id
    Given new sending from respondent to internal
    When new the message is saved as draft
      And new the message is read
    Then new retrieved message thread id is equal to message id

  Scenario: Internal user saves a draft  when it is retrieved it should have a thread id equal to the msg id
    Given new sending from internal to respondent
    When new the message is saved as draft
      And new the message is read
    Then new retrieved message thread id is equal to message id

  Scenario: Respondent saves a draft verify a msg_id is returned
    Given new sending from respondent to internal
    When new the message is saved as draft
    Then new response includes a msg_id

  Scenario: Internal user saves a draft  verify a msg_id is returned
    Given new sending from internal to respondent
    When new the message is saved as draft
    Then new response includes a msg_id


  Scenario: Respondent saves a draft without specifying an etag should receive a 201
    Given new sending from respondent to internal
    When new the message is saved as draft
    Then a created status code (201) is returned
     And  new the response should include a valid etag

  Scenario: Internal user saves a draft  without specifying an etag should receive a 201
    Given new sending from internal to respondent
    When new the message is saved as draft
    Then a created status code (201) is returned
     And  new the response should include a valid etag

  Scenario: Respondent saves a draft with specifying an etag should receive a 201 and an etag in the response
    Given new sending from respondent to internal
      And  new an etag is requested with an empty value
    When new the message is saved as draft
    Then a created status code (201) is returned
      And  new the response should include a valid etag

  Scenario: Internal user saves a draft  with an specifying etag should receive a 201 and an etag in the response
    Given new sending from internal to respondent
      And  new an etag is requested with an empty value
    When new the message is saved as draft
    Then a created status code (201) is returned
      And  new the response should include a valid etag

  Scenario: A Respondent saves a draft with an incorrect etag should receive a 409
    Given new sending from respondent to internal
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the message is read
      And  new an etag is requested with a value of 'INVALIDETAG'
    When   new the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: An Internal user saves a draft with an incorrect etag should receive a 409
    Given  new sending from internal to respondent
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new an etag is requested with a value of 'INVALIDETAG'
    When   new the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: A Respondent saves a draft with a correct etag
    Given new sending from respondent to internal
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new an etag is requested
    When   new the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: An Internal user saves a draft with with a correct etag
    Given  new sending from internal to respondent
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new an etag is requested
    When   new the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: A Respondent saves a draft then changes the body and updates the draft with the original etag
    Given new sending from respondent to internal
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new an etag is requested
      And  new the body is set to '--New body--'
    When   new the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: An Internal user saves a draft then changes the body and updates the draft with the original etag
    Given  new sending from internal to respondent
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new an etag is requested
      And  new the body is set to '--New body--'
    When   new the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: A Respondent saves a draft then changes the body and updates the draft with the new etag
    Given new sending from respondent to internal
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new the body is set to '--New body--'
      And  new an etag is requested
    When   new the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: An Internal user saves a draft then changes the body and updates the draft with the new etag
    Given  new sending from internal to respondent
      And  new an etag is requested with an empty value
      And  new the message is saved as draft
      And  new the draft is read
      And  new the body is set to '--New body--'
      And  new an etag is requested
    When   new the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: A Respondent saves a message and an internal user replies , the thread id should not equal the message id
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the user is set as internal
      And  new the draft is read
      And  new the from is set to internal
      And  new the to is set to respondent
      And  new the body is set to '--New body--'
      And  new the thread id is set to the last returned thread id
    When   new the message is saved as draft
    Then  a created status code (201) is returned
      And  new retrieved message thread id is not equal to message id

  Scenario: An Internal user saves a message and a respondent replies , the thread id should not equal the message id
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the user is set as respondent
      And  new the draft is read
      And  new the from is set to respondent
      And  new the to is set to internal
      And  new the body is set to '--New body--'
      And  new the thread id is set to the last returned thread id
    When  new the message is saved as draft
    Then   a created status code (201) is returned
      And  new retrieved message thread id is not equal to message id

    Scenario: A Respondent sends a message and an internal user saves draft then sends as reply validate thread id is correct
    Given new sending from respondent to internal
      And  new the message is sent
      And  new the user is set as internal
      And  new the message is read
      And  new the from is set to internal
      And  new the to is set to respondent
      And  new the body is set to '--New body--'
      And  new the thread id is set to the last returned thread id
      And  new the message is saved as draft
      And  new the draft is read
    When  new the message is sent
    Then  a created status code (201) is returned
      And  new retrieved message thread id is not equal to message id
      And  new the thread id is equal in all responses


    Scenario: An internal user sends a message and a respondent saves draft then sends as reply validate thread id is correct
    Given new sending from internal to respondent
      And  new the message is sent
      And  new the user is set as respondent
      And  new the message is read
      And  new the from is set to respondent
      And  new the to is set to internal
      And  new the body is set to '--New body--'
      And  new the thread id is set to the last returned thread id
      And  new the message is saved as draft
      And  new the draft is read
    When  new the message is sent
    Then  a created status code (201) is returned
      And  new retrieved message thread id is not equal to message id
      And  new the thread id is equal in all responses
