Feature: Message Send Endpoint

  Scenario: Submitting a valid message and receiving a 201
    Given a valid message
    When a message is sent
    Then a 201 status code is the response

  Scenario: Submit a message with a missing "To" field and receive a 400 error
    Given a message with an empty "To" field
    When a message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "From" field and receive a 400 error
    Given a message with an empty "From" field
    When a message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "Body" field and receive a 400 error
    Given a message with an empty "Body" field
    When a message is sent
    Then a 400 error status is returned

  Scenario: Submit a message with a missing "Subject" field and receive a 400
    Given a message with an empty "Subject" field
    When a message is sent
    Then a 400 error status is returned

  Scenario: Message sent without a thread id
    Given a message is sent with an empty "Thread ID"
    When a message is sent
    Then a 201 status code is the response

  Scenario: Message sent with a urn_to too long
    Given a message is sent with a urn_to which exceeds the max limit
    When a message is sent
    Then a 400 error status is returned

  Scenario: Message sent with a msg_from too long
    Given a message is sent with a urn_from which exceeds the field length
    When a message is sent
    Then a 400 error status is returned




