Feature: Message Send Endpoint

  Scenario: Submitting a valid message and receiving a 201
    Given a valid message
    When the message is sent
    Then a 201 status code is the response

  Scenario: Send a draft and receive a 201
    Given a message is identified as a draft
    When the draft is sent
    Then a 201 status code is the response

  Scenario: Send a draft and receive a msg_id
    Given a message is identified as a draft
    When the draft is sent
    Then a msg_id in the response

  Scenario: Send a draft and receive a thread_id
    Given a message is identified as a draft
    When the draft is sent
    Then a thread_id in the response

  Scenario: Submit a message with a missing "To" field and receive a 400 error
    Given  the 'To' field is empty
    When the message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "From" field and receive a 400 error
    Given the 'From' field is empty
    When the message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "Body" field and receive a 400 error
    Given the 'Body' field is empty
    When the message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "Subject" field and receive a 400
    Given the 'Subject' field is empty
    When the message is sent
    Then a 400 error status is returned

  Scenario: Message sent without a thread id
    Given the 'Thread ID' field is empty
    When the message is sent
    Then a 201 status code is the response

  Scenario: Message sent with a msg_to too long
    Given the 'To' field exceeds max limit in size
    When the message is sent
    Then a 400 error status is returned

  Scenario: Message sent with a msg_from too long
    Given the 'From' field exceeds max limit in size
    When the message is sent
    Then a 400 error status is returned

  Scenario: Message sent with an empty survey field return 400
    Given the survey field is empty
    When the message is sent
    Then a 400 error status is returned

  Scenario: Send a message with a msg_id not valid draft return 400
    Given a message contains a msg_id and is not a valid draft
    When the message is sent
    Then a 400 error status is returned

  Scenario: When a message with the label of "Draft" is sent and another user is trying to send the same message return a 409
    Given a draft message is posted
    When another user tries to send the same message
    Then is shown a 409 error status


  Scenario: A Etag is not present within the header
    Given a message is created
    When the message is sent with no Etag
    Then a 201 status code is the response
