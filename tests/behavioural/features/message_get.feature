Feature: Message get by ID Endpoint

   @ignore
  Scenario Outline: Retrieve a correct message with message ID
    Given there is a message to be retrieved
    When the get request is made with a correct message id
    Then a 200 HTTP response is returned
    And returned message field <field> is correct

   Examples: Fields
    |field  |
    |urn_to |
    |urn_from |
    |body    |
    |subject |
    |ReportingUnit   |
    |CollectionCase  |

  @ignore
  Scenario Outline: Retrieve a draft message
    Given there is a draft message to be retrieved
    When the get request is made with a draft message id
    Then a 200 HTTP response is returned
    And message returned is a draft

  @ignore
  Scenario Outline: Retrieve the correct draft message
    Given there is a draft message to be retrieved
    When the get request is made with a draft message id
    Then a 200 HTTP response is returned
    And returned message field <field> is correct

   Examples: Fields
    |field  |
    |urn_to |
    |urn_from |
    |body    |
    |subject |
    |ReportingUnit   |
    |CollectionCase  |

  Scenario: Retrieve a message with incorrect message ID
    Given there is a message to be retrieved
    When the get request has been made with an incorrect message id
    Then a 404 HTTP response is returned

  Scenario: Respondent sends message and retrieves the same message with it's labels
    Given a respondent sends a message
    When the respondent wants to see the message
    Then the retrieved message should have the label SENT

  Scenario: Internal user sends message and retrieves the same message with it's labels
    Given an internal user sends a message
    When the internal user wants to see the message
    Then the retrieved message should have the label SENT

  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
    Given an internal user sends a message
    When the respondent wants to see the message
    Then the retrieved message should have the labels INBOX and UNREAD

  Scenario: Respondent sends message and internal user retrieves the same message with it's labels
    Given a respondent sends a message
    When the internal user wants to see the message
    Then the retrieved message should have the labels INBOX and UNREAD 

  @ignore
  Scenario: As an internal user I want to be able to view a message from my drafts
    Given an internal user has created and saved a draft message
    When the internal user navigates to draft messages and opens the draft message
    Then the draft message should be displayed

  @ignore
  Scenario: As an External user I would like to be able to view a message from drafts
    Given an external user has created and saved a draft message
    When the external user navigates to draft messages and opens the draft message
    Then the draft message should be displayed
