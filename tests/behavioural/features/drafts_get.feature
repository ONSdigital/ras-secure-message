Feature: Get Drafts

  @ignore
  Scenario: User requests list of drafts
    Given the user has created and saved multiple drafts
    When the user requests drafts
    Then all the users drafts are returned

  @ignore
  Scenario: User not authorised to view drafts
    Given the user is not allowed to view drafts
    When the user requests drafts
    Then the user is forbidden