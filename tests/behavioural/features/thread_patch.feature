Feature: Threads patch endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

Scenario: Respondent starts a conversation , some to group/user,  internal closes the conversation
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the last returned thread is closed
Then a success status code no content 204 is returned