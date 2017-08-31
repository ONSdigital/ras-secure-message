Feature: Draft Put Endpoint

   Background: Reset database
    Given database is reset
      And using mock party service
     And using mock case service


  Scenario: A Respondent saves and edits a draft
    Given  new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to 'Some new body text'
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft
    Given  new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to 'Some new body text'
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

   Scenario: A Respondent saves and edits a draft with an apostraphe
    Given  new sending from respondent to internal
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to include an apostrophe
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

  Scenario: An internal user saves and edits a draft with an apostraphe
    Given  new sending from internal to respondent
      And  new the message is saved as draft
      And  new the draft is read
    When new the body is set to include an apostrophe
      And new the message is saved as draft
      And  new the draft is read
    Then new retrieved message body is as was saved

  @ignore

  Scenario: A user edits a draft that has not been previously saved
    Given a user edits a non-existing draft
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: A user edits a draft that has a too large to attribute
    Given a user modifies a draft with a to attribute that is too big
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: A user edits a draft that has a too large from attribute
    Given a user modifies a draft with a from attribute that is too big
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: A user edits a draft that has a too large body attribute
    Given a user modifies a draft with a body attribute that is too big
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: A user edits a draft that has a too large subject attribute
    Given a user modifies a draft with a subject attribute that is too big
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: A user edits a draft not including a to attribute
    Given a user modifies a draft not adding a to attribute
    When the user saves the draft
    Then a success status code (200) is returned

  Scenario: A user edits a draft not including a body attribute
    Given a user modifies a draft not adding a body attribute
    When the user saves the draft
    Then a success status code (200) is returned

  Scenario: A user edits a draft not including a subject attribute
    Given a user modifies a draft not adding a subject attribute
    When the user saves the draft
    Then a success status code (200) is returned

  Scenario: A user edits a draft not including a thread id attribute
    Given a user modifies a draft not adding a thread id attribute
    When the user saves the draft
    Then a success status code (200) is returned

  Scenario: A user edits a draft where msg id in url and in the message body do not match
    Given a user tries to modify a draft with mismatched msg ids
    When the user saves the draft
    Then a bad request status code (400) is returned

  Scenario: User retrieves etag from the header when modifying a draft
    Given there is a draft to be modified
    When the user modifies the draft
    Then a new etag should be returned to the user

  Scenario: A user is editing a draft while another user tries to modify the same draft
    Given a draft message is being edited
    When another user tries to modify the same draft message
    Then a conflict error status code (409) is returned

  Scenario: Edit draft without an etag present within the header
    Given there is a draft to be modified
    When the user edits the draft without etag
    Then a success status code (200) is returned