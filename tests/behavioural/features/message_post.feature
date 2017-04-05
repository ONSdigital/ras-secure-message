Feature: Message Send Endpoint

  Scenario: Submitting a valid message and receiving a 201
    Given a valid message
    When it is sent
    Then a 201 HTTP response is returned

  Scenario: Submit a message with a missing "To" field and receive a 400 error
    Given a message with an empty "To" field
    When it is sent a
    Then a 400 HTTP response is returned

  Scenario: Submit a message with a missing "From" field and receive a 400 error
    Given a message with an empty "From" field
    When it is sent x
    Then a 400 HTTP response is returned as the response afterwards

  Scenario: Submit a message with a missing "Body" field and receive a 400 error
    Given a message with an empty "Body" field
    When it is sent n
    Then a 400 HTTP response is returned as a response after

  Scenario: Submit a message with a missing "Subject" field and receive a 400
    Given a message with an empty "Subject" field
    When it is sent m
    Then a 400 HTTP response is returned as a response

  Scenario: Message sent without a thread id
    Given a message is sent with an empty "Thread ID"
    When it is sent z
    Then a 201 status code is the response

  Scenario: Setting a message archived status as "false" and receive a 201
    Given a message is marked as archived
    When it is sent v
    Then a 201 response is received

  Scenario: Setting a message read status as "false" and receive a 201
    Given a message is marked as read
    When it is sent e
    Then a 201 response is acquired