Feature: Message Send Endpoint

    Scenario: Submitting a valid message and receiving a 201
        Given a valid message is sent
        When the user submits the message
        Then a 201 HTTP response is returned

    Scenario: Submit a message with a missing "To" field and receive a 404 error
        Given a message is sent
        When the "To" field is missing
        Then a 400 HTTP response is returned

    Scenario: Submit a message with a missing "From" field and receive a 400 error
        Given a message is sent
        When the "From" field is missing
        Then a 400 HTTP response is returned

    Scenario: Submit a message with a missing "Body" field and receive a 400 error
        Given a message is sent
        When the "Body" field is missing
        Then a 400 HTTP response is returned

    Scenario: Submit a message with a missing "Subject" field and receive a 201 error
        Given a message is sent
        When the "Subject" field is missing
        Then a 201 HTTP response is returned

    Scenario: Message sent without a thread id
        Given a message is sent without a Thread id
	    Then a 201 status code is the response
        