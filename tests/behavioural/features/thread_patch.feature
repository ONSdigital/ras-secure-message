Feature: Threads patch endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

Scenario: Respondent starts a conversation , some to group/user,  internal closes the conversation
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the last returned thread is closed
Then a success status code no content 204 is returned

Scenario: Internal user closing an already closed conversation results in an error
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the last returned thread is closed
  And the last returned thread is closed
Then a bad request status code 400 is returned

Scenario: Internal user can change category of thread
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the category of the thread is changed to 'TECHNICAL'
Then a success status code no content 204 is returned

Scenario: Internal user changing category to unknown category results in an error
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the category of the thread is changed to 'FAKE'
Then a bad request status code 400 is returned
