Feature: Message Send Endpoint

 Background: Reset database
    Given using mock party service

  Scenario: Submitting a valid message and receiving a 201
    Given a valid message
    When the message is sent
    Then a created status code (201) is returned

  Scenario: Send a draft and receive a 201
    Given a message is identified as a draft
    When the draft is sent
    Then a created status code (201) is returned

  Scenario: Send a draft and receive a msg_id
    Given a message is identified as a draft
    When the draft is sent
    Then a created status code (201) is returned

  Scenario: A user sends a previously saved draft
    Given a user retrieves a previously saved draft
    When the draft is sent
    Then a created status code (201) is returned

  Scenario: Send a draft and receive a thread_id
    Given a message is identified as a draft
    When the draft is sent
    Then a thread_id in the response
    And thread_id is the same as msg_id

  Scenario: Send a draft and receive a msg_id
    Given a message is identified as a draft
    When the draft is sent
    Then a msg_id in the response

  Scenario: Send a draft which is a reply to another message
      Given a message is identified as a draft which is a reply to another message
      When the draft is sent
      Then thread_id is not the same as msg_id

  Scenario: Submit a message with a missing "To" field and receive a 400 error
    Given  the 'To' field is empty
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Submit a message with a missing "From" field and receive a 400 error
    Given the 'From' field is empty
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Submit a message with a missing "Body" field and receive a 400 error
    Given the 'Body' field is empty
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Submit a message with a missing "Subject" field and receive a 400
    Given the 'Subject' field is empty
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Message sent without a thread id
    Given the 'Thread ID' field is empty
    When the message is sent
    Then a created status code (201) is returned

  Scenario: Message sent with a msg_to too long
    Given the 'To' field exceeds max limit in size
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Message sent with a msg_from too long
    Given the 'From' field exceeds max limit in size
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Message sent with an empty survey field return 400
    Given the survey field is empty
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: Send a message with a msg_id not valid draft return 400
    Given a message contains a msg_id and is not a valid draft
    When the message is sent
    Then a bad request status code (400) is returned

  Scenario: When a message with the label of "Draft" is sent and another user is trying to send the same message return a 409
    Given a draft message is posted
    When another user tries to send the same message
    Then a conflict error status code (409) is returned

  Scenario: A Etag is not present within the header
    Given a message is created
    When the message is sent with no Etag
    Then a created status code (201) is returned

  Scenario: Send a message where msg_to is a string
    Given a msg_to is entered as a string
    When the message is sent with msg_to string
    Then a bad request status code (400) is returned

