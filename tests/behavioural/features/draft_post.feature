Feature: Draft Save Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: Respondent saves a draft and receives a 201
    Given sending from respondent to internal bres user
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: An internal user saves a draft and receives a 201
    Given sending from internal bres user to respondent
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Respondent saves a draft and receives a valid etag in the response
    Given sending from respondent to internal bres user
    When the message is saved as draft
    Then the response should include a valid etag

  Scenario: An internal user saves a draft and receives a valid etag in the response
    Given sending from internal bres user to respondent
    When the message is saved as draft
    Then the response should include a valid etag

  Scenario: Respondent saves a draft with an empty body , should receive a 201
    Given sending from respondent to internal bres user
      And  the body is set to empty
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Internal user saves a draft with an empty body , should receive a 201
    Given sending from internal bres user to respondent
      And  the body is set to empty
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Respondent saves a draft with a msg_id , should receive a 400
    Given sending from respondent to internal bres user
      And  the msg_id is set to '12345678'
    When the message is saved as draft
    Then a bad request status code (400) is returned

   Scenario: Internal user saves a draft with a msg_id , should receive a 400
    Given sending from internal bres user to respondent
      And  the msg_id is set to '12345678'
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with to too long should receive a 400
    Given sending from respondent to internal bres user
      And  the to field is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with to too long should receive a 400
    Given sending from internal bres user to respondent
      And  the to field is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an empty to field , should receive a 201
    Given sending from respondent to internal bres user
      And  the to is set to empty
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Internal user saves a draft with an empty to field , should receive a 201
    Given sending from internal bres user to respondent
      And the to is set to empty
    When the message is saved as draft
    Then a created status code (201) is returned

  Scenario: Respondent saves a draft from too long should receive a 400
    Given sending from respondent to internal bres user
      And  the from is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft from too long should receive a 400
    Given sending from internal bres user to respondent
      And  the from is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft body too long should receive a 400
    Given sending from respondent to internal bres user
      And  the body is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft body too long should receive a 400
    Given sending from internal bres user to respondent
      And  the body is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft subject too long should receive a 400
    Given sending from respondent to internal bres user
      And  the subject is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft subject too long should receive a 400
    Given sending from internal bres user to respondent
      And  the subject is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with missing from field should receive a 400 error
    Given the user is set as respondent
      And  the from is set to empty
      And  the to is set to internal bres user
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with missing from field should receive a 400 error
    Given the user is set as internal
      And  the from is set to empty
      And  the to is set to respondent
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with not their id is not in the from field should receive a 400 error
    Given the user is set as respondent
      And the from is set to alternative respondent
      And the to is set to internal bres user
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal User saves a draft with not their id is not in the from field should receive a 400 error
    Given the user is set as internal
      And the from is set to internal non bres user
      And the to is set to respondent
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an empty survey field and receive a 400 error
    Given sending from respondent to internal bres user
      And  the survey is set to empty
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an empty survey field and receive a 400 error
    Given sending from internal bres user to respondent
      And  the survey is set to empty
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft with an collection case field too large and receive a 400 error
    Given sending from respondent to internal bres user
      And  the collection case is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an collection case field too large and receive a 400 error
    Given sending from internal bres user to respondent
      And  the collection case is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned


  Scenario: Respondent saves a draft with an collection exercise field too large and receive a 400 error
    Given sending from respondent to internal bres user
      And  the collection exercise is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Internal user saves a draft with an collection exercise field too large and receive a 400 error
    Given sending from internal bres user to respondent
      And  the collection exercise is too long
    When the message is saved as draft
    Then a bad request status code (400) is returned

  Scenario: Respondent saves a draft  when it is retrieved it should have a thread id equal to the msg id
    Given sending from respondent to internal bres user
    When the message is saved as draft
      And the message is read
    Then retrieved message thread id is equal to message id

  Scenario: Internal user saves a draft  when it is retrieved it should have a thread id equal to the msg id
    Given sending from internal bres user to respondent
    When the message is saved as draft
      And the message is read
    Then retrieved message thread id is equal to message id

  Scenario: Respondent saves a draft verify a msg_id is returned
    Given sending from respondent to internal bres user
    When the message is saved as draft
    Then response includes a msg_id

  Scenario: Internal user saves a draft  verify a msg_id is returned
    Given sending from internal bres user to respondent
    When the message is saved as draft
    Then response includes a msg_id


  Scenario: Respondent saves a draft without specifying an etag should receive a 201
    Given sending from respondent to internal bres user
    When the message is saved as draft
    Then a created status code (201) is returned
     And  the response should include a valid etag

  Scenario: Internal user saves a draft  without specifying an etag should receive a 201
    Given sending from internal bres user to respondent
    When the message is saved as draft
    Then a created status code (201) is returned
     And  the response should include a valid etag

  Scenario: Respondent saves a draft with specifying an etag should receive a 201 and an etag in the response
    Given sending from respondent to internal bres user
      And  an etag is requested with an empty value
    When the message is saved as draft
    Then a created status code (201) is returned
      And  the response should include a valid etag

  Scenario: Internal user saves a draft  with an specifying etag should receive a 201 and an etag in the response
    Given sending from internal bres user to respondent
      And  an etag is requested with an empty value
    When the message is saved as draft
    Then a created status code (201) is returned
      And  the response should include a valid etag

  Scenario: A Respondent saves a draft with an incorrect etag should receive a 409
    Given sending from respondent to internal bres user
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the message is read
      And  an etag is requested with a value of 'INVALIDETAG'
    When   the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: An Internal user saves a draft with an incorrect etag should receive a 409
    Given  sending from internal bres user to respondent
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  an etag is requested with a value of 'INVALIDETAG'
    When   the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: A Respondent saves a draft with a correct etag
    Given sending from respondent to internal bres user
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  an etag is requested
    When   the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: An Internal user saves a draft with with a correct etag
    Given  sending from internal bres user to respondent
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  an etag is requested
    When   the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: A Respondent saves a draft then changes the body and updates the draft with the original etag
    Given sending from respondent to internal bres user
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  an etag is requested
      And  the body is set to '--New body--'
    When   the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: An Internal user saves a draft then changes the body and updates the draft with the original etag
    Given  sending from internal bres user to respondent
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  an etag is requested
      And  the body is set to '--New body--'
    When   the previously returned draft is modified
    Then   a success status code (200) is returned

  Scenario: A Respondent saves a draft then changes the body and updates the draft with the etag
    Given sending from respondent to internal bres user
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  the body is set to '--New body--'
      And  an etag is requested
    When   the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: An Internal user saves a draft then changes the body and updates the draft with the etag
    Given  sending from internal bres user to respondent
      And  an etag is requested with an empty value
      And  the message is saved as draft
      And  the draft is read
      And  the body is set to '--New body--'
      And  an etag is requested
    When   the previously returned draft is modified
    Then   a conflict error status code (409) is returned

  Scenario: A Respondent saves a message and an internal user replies , the thread id should not equal the message id
    Given sending from respondent to internal bres user
      And  the message is saved as draft
      And  the user is set as internal
      And  the draft is read
      And  the from is set to internal bres user
      And  the to is set to respondent
      And  the body is set to '--New body--'
      And  the thread id is set to the last returned thread id
    When   the message is saved as draft
    Then  a created status code (201) is returned
      And  retrieved message thread id is not equal to message id

  Scenario: An Internal user saves a message and a respondent replies , the thread id should not equal the message id
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the message is read
      And  the from is set to respondent
      And  the to is set to internal bres user
      And  the body is set to '--New body--'
      And  the thread id is set to the last returned thread id
    When  the message is saved as draft
    Then   a created status code (201) is returned
      And  retrieved message thread id is not equal to message id

    Scenario: A Respondent sends a message and an internal user saves draft then sends as reply validate thread id is correct
    Given sending from respondent to internal bres user
      And  the message is sent
      And  the user is set as internal
      And  the message is read
      And  the from is set to internal bres user
      And  the to is set to respondent
      And  the body is set to '--New body--'
      And  the thread id is set to the last returned thread id
      And  the message is saved as draft
      And  the draft is read
    When  the message is sent
    Then  a created status code (201) is returned
      And  retrieved message thread id is not equal to message id
      And  the thread id is equal in all responses

    Scenario: An internal user sends a message and a respondent saves draft then sends as reply validate thread id is correct
    Given sending from internal bres user to respondent
      And  the message is sent
      And  the user is set as respondent
      And  the message is read
      And  the from is set to respondent
      And  the to is set to internal bres user
      And  the body is set to '--New body--'
      And  the thread id is set to the last returned thread id
      And  the message is saved as draft
      And  the draft is read
    When  the message is sent
    Then  a created status code (201) is returned
      And  retrieved message thread id is not equal to message id
      And  the thread id is equal in all responses
