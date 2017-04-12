Feature: Message Send Endpoint

  Scenario: Submitting a valid message and receiving a 201
    Given a valid message
    When it is sent
    Then a 201 HTTP response is returned

  Scenario: Submit a message with a missing "To" field and receive a 400 error
    Given a message with an empty "To" field
    When it is sent
    Then a 400 HTTP response is returned

  Scenario: Submit a message with a missing "From" field and receive a 400 error
    Given a message with an empty "From" field
    When it is sent
    Then a 400 HTTP response is returned as the response afterwards

  Scenario: Submit a message with a missing "Body" field and receive a 400 error
    Given a message with an empty "Body" field
    When it is sent
    Then a 400 HTTP response is returned as a response after

  Scenario: Submit a message with a missing "Subject" field and receive a 400
    Given a message with an empty "Subject" field
    When it is sent
    Then a 400 HTTP response is returned as a response

  Scenario: Message sent without a thread id
    Given a message is sent with an empty "Thread ID"
    When it is sent
    Then a 201 status code is the response

  Scenario: Message sent with a urn_to too long
    Given a message is sent with a urn_to which exceeds the max limit
    When the message is sent
    Then a 400 error status is given

  Scenario: Message sent with a msg_from too long
    Given a message is sent with a urn_from which exceeds the field length
    When a message is sent
    Then a 400 error is given



