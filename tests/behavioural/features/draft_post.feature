Feature: Draft Save Endpoint

  Scenario: Save a valid draft get a 201 return
    Given a valid draft
    When the draft is saved
    Then a 201 status code is the response
    And an etag should be sent with the draft

  Scenario: Save a draft with body field empty return 201
    Given a draft has an body field set to empty
    When the draft is saved
    Then a 201 status code is the response

  Scenario: Save a draft with a message ID will return 400
    Given a draft including a msg_id
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with to field too large return 400
    Given a draft with to field too large in size
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with from field too large return 400
    Given a draft with from field too large in size
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with body field too large return 400
    Given a draft with body field too large in size
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with subject field too large return 400
    Given a draft with subject field too large in size
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with an empty from field return 400
    Given a draft with a from field set as empty
    When the draft is saved
    Then a 400 error status is returned

  Scenario: Save a draft with an empty survey field return 400
    Given a draft with a survey field set as empty
    When the draft is saved
    Then a 400 error status is returned

  Scenario: As a user I would like a new draft message not related to a thread to be given the message id as a thread id
    Given A user creates a draft that is not associated with a thread
    When the draft is saved
    Then the thread id should be set to the message id

  Scenario: As a user the message id for my saved draft should be returned when saving a draft
    Given a user creates a valid draft
    When the user saves this draft
    Then the message id should be returned in the response

