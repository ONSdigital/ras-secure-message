Feature: Message get by ID Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario Outline: Respondent saves and retrieves a message verify the message fields are as sent
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

   Examples: Fields
    |field  |
    |msg_to |
    |msg_from |
    |body    |
    |subject |
    |ru   |
    |Collection Case  |
    |Collection Exercise  |
    |survey              |

  Scenario Outline: Internal user saves and retrieves a message verify the message fields are as sent
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

   Examples: Fields
    |field  |
    |msg_to |
    |msg_from |
    |body    |
    |subject |
    |ru   |
    |Collection Case  |
    |Collection Exercise  |
    |survey              |



  Scenario: Respondent saves and retrieves a message verify the thread_id is the same as message id
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message thread id is equal to message id

  Scenario: Internal user saves and retrieves a message verify the thread_id is the same as message id
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message thread id is equal to message id


  Scenario: Respondent saves and retrieves a message verify the message from additional data  (@msg_from) is as expected
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message additional from data matches that from party service

  Scenario: Internal user saves and retrieves a message verify the message to additional data  (@msg_to) is as expected
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message additional to data matches that from party service

  Scenario: Respondent saves and retrieves a message verify the message ru additional data  (@ru) is as expected
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message additional ru_id data matches that from party service


  Scenario: Internal user saves and retrieves a message verify the message ru additional data  (@ru) is as expected
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the message is read
    Then a success status code (200) is returned
      And  retrieved message additional ru_id data matches that from party service

  Scenario: Respondent saves and retrieves a draft message verify it has a DRAFT label
    Given sending from respondent to internal bres user
      And   the message is saved as draft
    When  the message is read
    Then a success status code (200) is returned
      And the response message has the label 'DRAFT'


  Scenario: Internal user saves and retrieves a draft message verify it has a DRAFT label
    Given sending from internal bres user to respondent
      And   the message is saved as draft
    When  the message is read
    Then a success status code (200) is returned
      And the response message has the label 'DRAFT'

  Scenario Outline: Respondent saves and retrieves a draft message verify the message fields are as sent
    Given sending from respondent to internal bres user
      And   the message is saved as draft
    When  the message is read
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

    Examples: Fields
     |field  |
     |msg_to |
     |msg_from |
     |body    |
     |subject |
     |ru   |
     |Collection Case  |
     |Collection Exercise  |
     |survey              |


  Scenario Outline: Internal user saves and retrieves a draft message verify the message fields are as sent
    Given sending from internal bres user to respondent
      And   the message is saved as draft
    When  the message is read
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

    Examples: Fields
     |field  |
     |msg_to |
     |msg_from |
     |body    |
     |subject |
     |ru   |
     |Collection Case  |
     |Collection Exercise  |
     |survey              |

  Scenario: Respondent retrieves a message with incorrect message ID
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message with id '12345678-ed43-4cdb-ad1c-450f9986859b' is retrieved
    Then  a not found status code (404) is returned

  Scenario: Internal user retrieves a message with incorrect message ID
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the message with id '12345678-ed43-4cdb-ad1c-450f9986859b' is retrieved
    Then  a not found status code (404) is returned

  Scenario: Respondent sends message and retrieves the same message with it's labels
    Given sending from respondent to internal bres user
      And   the message is sent
    When  the message is read
    Then  the response message has the label 'SENT'

  Scenario: Internal user sends message and retrieves the same message with it's labels
    Given sending from internal bres user to respondent
    When  the message is sent
      And   the message is read
    Then  the response message has the label 'SENT'

Scenario: Respondent sends message and internal user retrieves the same message with it's labels
  Given   sending from respondent to internal bres user
      And   the message is sent
    When  the user is set as internal
      And   the message is read
    Then  the response message has the label 'INBOX'
      And   the response message has the label 'UNREAD'
      And   the response message should a label count of '2'

  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
    Given sending from internal bres user to respondent
      And   the message is sent
    When  the user is set as respondent
      And   the message is read
    Then  the response message has the label 'INBOX'
      And   the response message has the label 'UNREAD'
      And   the response message should a label count of '2'

  Scenario: Respondent attempts to read a message they did not send or receive
    Given sending from respondent to internal bres user
    When  the message is sent
      And   the user is set as alternative respondent
      And   the message is read
    Then a forbidden status code (403) is returned

  Scenario: Internal user sends message and retrieves it , should be marked as from_internal True
    Given sending from internal bres user to respondent
    When the message is sent
      And the message is read
    Then a success status code (200) is returned
      And sent from internal is 'True'

  Scenario: Internal user sends message and external user retrieves it , should be marked as from_internal True
    Given sending from internal bres user to respondent
    When the message is sent
      And the user is set as respondent
      And the message is read
    Then a success status code (200) is returned
      And sent from internal is 'True'

    Scenario: External user sends message and retrieves it , should be marked as from_internal False
    Given sending from respondent to internal bres user
    When the message is sent
      And the message is read
    Then a success status code (200) is returned
      And sent from internal is 'False'

  Scenario: External user sends message and internal user retrieves it , should be marked as from_internal False
    Given sending from respondent to internal bres user
    When the message is sent
      And the user is set as internal
      And the message is read
    Then a success status code (200) is returned
      And sent from internal is 'False'
