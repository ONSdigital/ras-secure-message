Feature: Message Send Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: Respondent sending a valid message and receiving a 201
    Given new sending from respondent to internal
    When new the message is sent
    Then a created status code (201) is returned

  Scenario: Internal user sending a valid message and receiving a 201
    Given new sending from internal to respondent
    When new the message is sent
    Then a created status code (201) is returned

  Scenario: Respondent send a message without a thread id and other fields correct then they should receive a 201
    Given new sending from respondent to internal
    When new the message is sent
    Then a created status code (201) is returned

  Scenario: Internal user  send a message without a thread id and other fields correct then they should receive a 201
    Given new sending from internal to respondent
    When new the message is sent
    Then a created status code (201) is returned

  Scenario: Respondent sending a message with missing to field should receive a 400 error
    Given new the user is set as respondent
      And  new the from is set to respondent
      And  new the to is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sending a message with missing to field should receive a 400 error
    Given new the user is set as internal
      And  new the from is set to internal
      And  new the to is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Respondent sending a message with missing from field should receive a 400 error
    Given new the user is set as respondent
      And  new the from is set to empty
      And  new the to is set to internal
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sending a message with missing from field should receive a 400 error
    Given new the user is set as internal
      And  new the from is set to empty
      And  new the to is set to respondent
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Respondent sending a message with a missing "Body" field and receive a 400 error
    Given new sending from respondent to internal
      And  new the body is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sending a message with a missing "Body" field and receive a 400 error
    Given new sending from internal to respondent
      And  new the body is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Respondent sending a message with a missing subject field and receive a 400 error
    Given new sending from respondent to internal
      And  new the subject is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sending a message with a missing subject field and receive a 400 error
    Given new sending from internal to respondent
      And  new the subject is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned


  Scenario: Respondent send a message to too long should receive a 400
    Given new sending from respondent to internal
      And  new the to field is too long
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user send a message to too long should receive a 400
    Given new sending from internal to respondent
      And  new the to field is too long
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Respondent send a message from too long should receive a 400
    Given new sending from respondent to internal
      And  new the from is too long
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user send a message from too long should receive a 400
    Given new sending from internal to respondent
      And  new the from is too long
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Respondent sending a message with an empty survey field and receive a 400 error
    Given new sending from respondent to internal
      And  new the survey is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sending a message with an empty survey field and receive a 400 error
    Given new sending from internal to respondent
      And  new the survey is set to empty
    When new the message is sent
    Then a bad request status code (400) is returned


  Scenario: Respondent sends a message with a msg_id but is not a draft
    Given new sending from respondent to internal
      And  new the msg_id is set to '12345678'
    When new the message is sent
    Then a bad request status code (400) is returned

  Scenario: Internal user sends a message with a msg_id but is not a draft
    Given new sending from internal to respondent
      And  new the msg_id is set to '12345678'
    When new the message is sent
    Then a bad request status code (400) is returned

 Scenario: Respondent sends a message with a msg_to set as a string not an array should receive a 400
    Given new the user is set as respondent
      And  new the from is set to respondent
      And  new the to is set to internal user as a string not array
    When new the message is sent
    Then a bad request status code (400) is returned

 Scenario: Internal user sends a message with a msg_to set as a string not an array should receive a 400
    Given new the user is set as internal
      And  new the from is set to internal
      And  new the to is set to respondent as a string not array
    When new the message is sent
    Then a bad request status code (400) is returned

 Scenario: Respondent sends a message with a msg_to set to an unknown user should receive a 400
    Given new the user is set as respondent
      And  new the from is set to respondent
      And  new the to is set to 'someone_who_does_not_exist'
    When new the message is sent
    Then a bad request status code (400) is returned

 Scenario: Internal user sends a message with a msg_to to an unknown user should receive a 400
    Given new the user is set as internal
      And  new the from is set to internal
      And  new the to is set to 'someone_who_does_not_exist'
    When new the message is sent
    Then a bad request status code (400) is returned

