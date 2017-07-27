Feature: Delete Draft By Id



  @ignore
  Scenario: A user deletes a draft that does not exist
    Given the user requests to delete a draft that does not exist
    When the draft is deleted
    Then a method not allowed error should be the response

  @ignore
  Scenario: A user deletes a draft they do not have permission to
    Given the user requests to delete a draft they don't have permission to
    When the draft is deleted
    Then the user is forbidden from action requested

  @ignore
  Scenario: A user deletes a draft
    Given the user requests to delete a draft
    When the draft is deleted
    Then the draft should be removed
    And a success status code (200) is returned
