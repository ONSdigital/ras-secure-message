Feature: Draft Put Endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario Outline: A Respondent saves and edits a draft
    Given  sending from respondent to internal <user>
      And  the message is saved as draft V2
      And  the draft is read V2
    When the body is set to 'Some body text'
      And the message is saved as draft V2
      And  the draft is read V2
    Then retrieved message body is as was saved

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: An internal user saves and edits a draft
    Given  sending from internal <user> to respondent
      And  the message is saved as draft V2
      And  the draft is read V2
    When the body is set to 'Some body text'
      And the message is saved as draft V2
      And  the draft is read V2
    Then retrieved message body is as was saved

    Examples: user type
    | user        |
    | specific user |
    | group        |

