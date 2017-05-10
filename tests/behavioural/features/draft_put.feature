Feature: Draft Put Endpoint

  Scenario: An existing draft is updated 200 is returned
    Given a valid draft has been modified
    When it is saved
    Then a 200 is returned

  Scenario: A new draft is updated
    Given a non-existing draft is modified
    When it is saved
    Then a 400 error status is returned

  Scenario: As an internal user I want to be able to edit a message from my drafts
    Given an internal user has opened a previously saved draft message
    When the internal user edits the content of the message and saves it as a draft
    Then the original draft message is replaced by the edited version

  Scenario: As an External user I would like to be able to edit a message from drafts
    Given an external user has opened a previously saved draft message
    When the external user edits the content of the message and saves it as a draft
    Then the original draft message is replaced by the edited version