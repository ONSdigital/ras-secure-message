Feature: Draft Save Endpoint

  Scenario: Save a valid draft get a 201 return
    Given a valid draft
    When the draft is saved
    Then a 201 status code is the response

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

  @ignore
  Scenario: As an External user I would like to be able to save a new message as draft
    Given an external user has created a secure message including 'subject' and selected 'save'
    When the user navigates to the draft inbox
    Then the draft message is displayed in the draft inbox
