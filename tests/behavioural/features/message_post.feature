Feature: Message Send Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: Respondent sending a valid message to BRES user and receiving a 201
    Given sending from respondent to internal bres user
    When the message is sent
    Then a created status code 201 is returned

  Scenario: Internal specific user sending a valid message and receiving a 201
    Given sending from internal specific user to respondent
    When the message is sent
    Then a created status code 201 is returned

  Scenario: Respondent send a message without a thread id and other fields correct then they should receive a 201
    Given sending from respondent to internal bres user
    When the message is sent
    Then a created status code 201 is returned

  Scenario: Internal user send a message without a thread id and other fields correct then they should receive a 201
    Given sending from internal specific user to respondent
    When the message is sent
    Then a created status code 201 is returned

  Scenario: Respondent sending a message with missing to field should receive a 400 error
    Given the user is set as respondent
      And  the from is set to respondent
      And  the to is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sending a message with missing to field should receive a 400 error
    Given the user is set as internal
      And  the from is set to internal specific user
      And  the to is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Respondent sending a message with missing from field should receive a 400 error
    Given the user is set as respondent
      And  the from is set to empty
      And  the to is set to internal specific user
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sending a message with missing from field should receive a 400 error
    Given the user is set as internal
      And  the from is set to empty
      And  the to is set to respondent
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Respondent sends a message and their id is not in the from field should receive a 400 error
    Given the user is set as respondent
      And the from is set to alternative respondent
      And the to is set to internal specific user
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal User sends a message and their id is not in the from field should receive a 400 error
    Given the user is set as internal
      And the from is set to internal non specific user
      And the to is set to respondent
    When the message is sent
    Then a bad request status code 400 is returned


  Scenario: Respondent sending a message with a missing "Body" field and receive a 400 error
    Given sending from respondent to internal bres user
      And  the body is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sending a message with a missing "Body" field and receive a 400 error
    Given sending from internal specific user to respondent
      And  the body is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Respondent sending a message with a missing subject field and receive a 400 error
    Given sending from respondent to internal bres user
      And  the subject is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sending a message with a missing subject field and receive a 400 error
    Given sending from internal specific user to respondent
      And  the subject is set to empty
    When the message is sent
    Then a bad request status code 400 is returned


  Scenario: Respondent send a message to too long should receive a 400
    Given sending from respondent to internal bres user
      And  the to field is too long
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user send a message to too long should receive a 400
    Given sending from internal specific user to respondent
      And  the to field is too long
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Respondent send a message from too long should receive a 400
    Given sending from respondent to internal bres user
      And  the from is too long
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user send a message from too long should receive a 400
    Given sending from internal specific user to respondent
      And  the from is too long
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Respondent sending a message with an empty survey field and receive a 400 error
    Given sending from respondent to internal bres user
      And  the survey is set to empty
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sending a message with an empty survey field and receive a 400 error
    Given sending from internal specific user to respondent
      And  the survey is set to empty
    When the message is sent
    Then a bad request status code 400 is returned


  Scenario: Respondent sends a message with a msg_id but is not a draft
    Given sending from respondent to internal bres user
      And  the msg_id is set to '12345678'
    When the message is sent
    Then a bad request status code 400 is returned

  Scenario: Internal user sends a message with a msg_id but is not a draft
    Given sending from internal specific user to respondent
      And  the msg_id is set to '12345678'
    When the message is sent
    Then a bad request status code 400 is returned

 Scenario: Respondent sends a message with a msg_to set as a string not an array should receive a 400
    Given the user is set as respondent
      And  the from is set to respondent
      And  the to is set to internal specific user as a string not array
    When the message is sent
    Then a bad request status code 400 is returned

 Scenario: Internal user sends a message with a msg_to set as a string not an array should receive a 400
    Given the user is set as internal
      And  the from is set to internal specific user
      And  the to is set to respondent as a string not array
    When the message is sent
    Then a bad request status code 400 is returned

 Scenario: Respondent sends a message with a msg_to set to an unknown user should receive a 400
    Given the user is set as respondent
      And  the from is set to respondent
      And  the to is set to 'someone_who_does_not_exist'
    When the message is sent
    Then a bad request status code 400 is returned

 Scenario: Internal user sends a message with a msg_to to an unknown user should receive a 400
    Given the user is set as internal
      And  the from is set to internal specific user
      And  the to is set to 'someone_who_does_not_exist'
    When the message is sent
    Then a bad request status code 400 is returned

