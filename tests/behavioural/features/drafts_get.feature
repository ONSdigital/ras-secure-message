Feature: Get Drafts

  Background: Reset database
    Given database is reset

  Scenario: User requests list of drafts
    Given the user has created and saved multiple drafts
    When the user requests drafts
    Then only the users drafts are returned

  Scenario: User requests second page of list of drafts
    Given the user has created and saved multiple drafts
    When the user requests second page of drafts
    Then user will get drafts from second page of pagination

  @ignore
  Scenario: User not authorised to view drafts
    Given the user is not allowed to view drafts
    When the user requests drafts
    Then the user is forbidden

  Scenario: Internal user saves multiple drafts and Respondent retrieves the list of drafts with particular collection case 
    Given an Internal user saves multiple drafts with different collection case 
    When the Respondent gets their drafts with particular collection case 
    Then the retrieved drafts should have the correct collection case

  Scenario: Internal user saves multiple drafts and Respondent retrieves the list of drafts with particular collection exercise 
    Given an Internal user saves multiple drafts with different collection exercise 
    When the Respondent gets their drafts with particular collection exercise 
    Then the retrieved drafts should have the correct collection exercise