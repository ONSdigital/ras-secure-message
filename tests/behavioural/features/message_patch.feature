Feature: Message patch endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

Scenario: Internal user can change survey_id in a thread
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the survey_id of the message is changed to 'f62ec9bb-0074-40de-b502-1b0cd2f72ef4'
Then a success status code no content 204 is returned

Scenario: Internal user changing survey_id to a non-uuid results in an error
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the survey_id of the message is changed to 'FAKE'
Then a bad request status code 400 is returned

Scenario: Internal user changing survey_id to empty string results in an error
Given sending from respondent to internal group
  And '1' messages are sent
When the user is set as internal specific user
  And the survey_id of the message is changed to an empty string
Then a bad request status code 400 is returned
