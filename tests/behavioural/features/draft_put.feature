Feature: Draft Put Endpoint

  @ignore
  Scenario: A user edits a previously saved draft
    Given a user edits a previously saved draft
    When the user saves the draft
    Then the draft stored includes the new changes
    And a success response is given

  Scenario: A user edits a draft that has not been previously saved
    Given a user edits a non-existing draft
    When the user saves the draft
    Then a bad request error is returned

  Scenario: A user edits a draft that has a too large to attribute
    Given a user modifies a draft with a to attribute that is too big
    When the user saves the draft
    Then a bad request error is returned

  Scenario: A user edits a draft that has a too large from attribute
    Given a user modifies a draft with a from attribute that is too big
    When the user saves the draft
    Then a bad request error is returned

  Scenario: A user edits a draft that has a too large body attribute
    Given a user modifies a draft with a body attribute that is too big
    When the user saves the draft
    Then a bad request error is returned

  Scenario: A user edits a draft that has a too large subject attribute
    Given a user modifies a draft with a subject attribute that is too big
    When the user saves the draft
    Then a bad request error is returned

  Scenario: A user edits a draft not including a to attribute
    Given a user modifies a draft not adding a to attribute
    When the user saves the draft
    Then a success response is given

  Scenario: A user edits a draft not including a body attribute
    Given a user modifies a draft not adding a body attribute
    When the user saves the draft
    Then a success response is given

  Scenario: A user edits a draft not including a subject attribute
    Given a user modifies a draft not adding a subject attribute
    When the user saves the draft
    Then a success response is given

  Scenario: A user edits a draft not including a thread id attribute
    Given a user modifies a draft not adding a thread id attribute
    When the user saves the draft
    Then a success response is given

  Scenario: A user edits a draft where msg id in url and in the message body do not match
    Given a user tries to modify a draft with mismatched msg ids
    When the user saves the draft
    Then a bad request error is returned

  @ignore
  Scenario: A etag is not present within the header
    Given a message is retrieved
    When there is no etag in the header
    Then a bad request error is returned

  Scenario: A user is editing a draft while another user tries to modify the same draft
    Given a draft message is being edited
    When another user tries to modify the same draft message
    Then a conflict error is returned