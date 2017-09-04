Feature: Draft Put Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario: A Respondent saves and edits a draft
    Given  sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
    When the body is set to 'Some body text'
      And the message is saved as draft
      And  the draft is read
    Then retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft
    Given  sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
    When the body is set to 'Some body text'
      And the message is saved as draft
      And  the draft is read
    Then retrieved message body is as was saved

   Scenario: A Respondent saves and edits a draft with an apostraphe
    Given  sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
    When the body is set to include an apostrophe
      And the message is saved as draft
      And  the draft is read
    Then retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft with an apostraphe
    Given  sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
    When the body is set to include an apostrophe
      And the message is saved as draft
      And  the draft is read
    Then retrieved message body is as was saved


  Scenario: A Respondent attempts to edit a draft that was previously saved as a message
    Given  sending from respondent to internal
      And  the message is sent
      And  the draft is read
    When   the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: An internal user attempts to edit a draft that was previously saved as a message
    Given  sending from internal to respondent
      And  the message is sent
      And  the draft is read
    When   the previously returned draft is modified
    Then a bad request status code (400) is returned

    # New Field validations

   Scenario: Respondent updates a draft with an empty body , should receive a 201
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the body is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Internal user updates a draft with an empty body , should receive a 201
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the body is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Respondent updates a draft with an empty subject , should receive a 201
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the subject is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Internal user updates a draft with an empty subject , should receive a 201
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the subject is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Respondent updates a draft with an invalid  msg_id , should receive a 400
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the msg_id is set to '12345678'
    When the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Internal user updates a draft with an invalid  msg_id , should receive a 400
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the msg_id is set to '12345678'
    When the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with to too long should receive a 400
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the to field is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with to too long should receive a 400
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the to field is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with an empty to field , should receive a 200
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the to is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Internal user updates a draft with an empty to field , should receive a 200
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And the to is set to empty
    When the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Respondent updates a draft from too long should receive a 400
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the from is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal updates saves a draft from too long should receive a 400
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the from is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft body too long should receive a 400
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the body is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal updates saves a draft body too long should receive a 400
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the body is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft subject too long should receive a 400
    Given sending from respondent to internal
     And  the message is saved as draft
     And  the draft is read
     And  the subject is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft subject too long should receive a 400
    Given sending from internal to respondent
     And  the message is saved as draft
     And  the draft is read
     And  the subject is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with missing from field should receive a 400 error
    Given the user is set as respondent
      And  the message is saved as draft
      And  the draft is read
      And  the from is set to empty
      And  the to is set to internal
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with missing from field should receive a 400 error
    Given the user is set as internal
      And  the message is saved as draft
      And  the draft is read
      And  the from is set to empty
      And  the to is set to respondent
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with an empty survey field and receive a 400 error
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
      And  the survey is set to empty
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an empty survey field and receive a 400 error
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
      And  the survey is set to empty
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with an collection case field too large and receive a 400 error
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
      And  the collection case is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an collection case field too large and receive a 400 error
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
      And  the collection case is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with an collection exercise field too large and receive a 400 error
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
      And  the collection exercise is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an collection exercise field too large and receive a 400 error
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
      And  the collection exercise is too long
    When the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft and adds a thread id
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
      And  the thread_id is set to '12345'
    When the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: An internal user updates a draft and adds a thread id
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
      And  the thread_id is set to '12345'
    When the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Respondent updates a draft where message id in url and body do not match
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
    When the previously returned draft is modified where data message id does not match url
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft where message id in url and body do not match
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
    When the previously returned draft is modified where data message id does not match url
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft should recieve an etag
    Given sending from respondent to internal
      And  the message is saved as draft
      And  the draft is read
    When the previously returned draft is modified
    Then the response should include a valid etag

  Scenario: Internal user updates a draft should recieve an etag
    Given sending from internal to respondent
      And  the message is saved as draft
      And  the draft is read
    When the previously returned draft is modified
    Then the response should include a valid etag



