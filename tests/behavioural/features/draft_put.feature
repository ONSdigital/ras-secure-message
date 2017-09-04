Feature: Draft Put Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario: A Respondent saves and edits a draft
    Given  new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to 'Some new body text'
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft
    Given  new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to 'Some new body text'
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

   Scenario: A Respondent saves and edits a draft with an apostraphe
    Given  new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to include an apostrophe
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft with an apostraphe
    Given  new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to include an apostrophe
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved


  Scenario: A Respondent attempts to edit a draft that was previously saved as a message
    Given  new sending from respondent to internal
      And  new the message is sent
      And  new the draft is read
    When   new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: An internal user attempts to edit a draft that was previously saved as a message
    Given  new sending from internal to respondent
      And  new the message is sent
      And  new the draft is read
    When   new the previously returned draft is modified
    Then a bad request status code (400) is returned

    # New Field validations

   Scenario: Respondent updates a draft with an empty body , should receive a 201
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the body is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Internal user updates a draft with an empty body , should receive a 201
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the body is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Respondent updates a draft with an empty subject , should receive a 201
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the subject is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Internal user updates a draft with an empty subject , should receive a 201
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the subject is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Respondent updates a draft with an invalid  msg_id , should receive a 400
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the msg_id is set to '12345678'
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Internal user updates a draft with an invalid  msg_id , should receive a 400
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the msg_id is set to '12345678'
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with to too long should receive a 400
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the to field is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with to too long should receive a 400
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the to field is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with an empty to field , should receive a 200
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the to is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Internal user updates a draft with an empty to field , should receive a 200
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And new the to is set to empty
    When new the previously returned draft is modified
    Then a success status code (200) is returned


  Scenario: Respondent updates a draft from too long should receive a 400
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the from is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal updates saves a draft from too long should receive a 400
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the from is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft body too long should receive a 400
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the body is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal updates saves a draft body too long should receive a 400
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the body is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft subject too long should receive a 400
    Given new sending from respondent to internal
     And  new the message is saved as draft
     And  new the draft is read
     And  new the subject is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft subject too long should receive a 400
    Given new sending from internal to respondent
     And  new the message is saved as draft
     And  new the draft is read
     And  new the subject is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with missing from field should receive a 400 error
    Given new the user is set as respondent
      And  new the message is saved as draft
      And  new the draft is read
      And  new the from is set to empty
      And  new the to is set to internal
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with missing from field should receive a 400 error
    Given new the user is set as internal
      And  new the message is saved as draft
      And  new the draft is read
      And  new the from is set to empty
      And  new the to is set to respondent
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with an empty survey field and receive a 400 error
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
      And  new the survey is set to empty
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an empty survey field and receive a 400 error
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
      And  new the survey is set to empty
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft with an collection case field too large and receive a 400 error
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
      And  new the collection case is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an collection case field too large and receive a 400 error
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
      And  new the collection case is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft with an collection exercise field too large and receive a 400 error
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
      And  new the collection exercise is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft with an collection exercise field too large and receive a 400 error
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
      And  new the collection exercise is too long
    When new the previously returned draft is modified
    Then a bad request status code (400) is returned


  Scenario: Respondent updates a draft and adds a thread id
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
      And  new the thread_id is set to '12345'
    When new the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: An internal user updates a draft and adds a thread id
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
      And  new the thread_id is set to '12345'
    When new the previously returned draft is modified
    Then a success status code (200) is returned

  Scenario: Respondent updates a draft where message id in url and body do not match
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the previously returned draft is modified where data message id does not match url
    Then a bad request status code (400) is returned

  Scenario: Internal user updates a draft where message id in url and body do not match
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the previously returned draft is modified where data message id does not match url
    Then a bad request status code (400) is returned

  Scenario: Respondent updates a draft should recieve an etag
    Given new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the previously returned draft is modified
    Then new the response should include a valid etag

  Scenario: Internal user updates a draft should recieve an etag
    Given new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the previously returned draft is modified
    Then new the response should include a valid etag



