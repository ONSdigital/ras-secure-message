Feature: Message get by ID Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services


  Scenario Outline: Respondent saves and retrieves a message verify the message fields are as sent
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And new retrieved message <field> is as was saved

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
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And new retrieved message <field> is as was saved

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
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message thread id is equal to message id

  Scenario: Internal user saves and retrieves a message verify the thread_id is the same as message id
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message thread id is equal to message id


  Scenario: Respondent saves and retrieves a message verify the message from additional data  (@msg_from) is as expected
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional from data matches that from party service


  Scenario: Internal user saves and retrieves a message verify the message from additional data  (@msg_from) is as expected
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional from data matches that from party service

  Scenario: Respondent saves and retrieves a message verify the message to additional data  (@msg_to) is as expected
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional to data matches that from party service

  Scenario: Internal user saves and retrieves a message verify the message to additional data  (@msg_to) is as expected
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional to data matches that from party service

  Scenario: Respondent saves and retrieves a message verify the message ru additional data  (@ru) is as expected
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional ru_id data matches that from party service


  Scenario: Internal user saves and retrieves a message verify the message ru additional data  (@ru) is as expected
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message is read
    Then a success status code (200) is returned
      And  new retrieved message additional ru_id data matches that from party service

  Scenario: Respondent saves and retrieves a draft message verify it has a DRAFT label
    Given new sending from respondent to internal
      And   new the message is saved as draft
    When  new the message is read
    Then a success status code (200) is returned
      And new the response message has the label 'DRAFT'


  Scenario: Internal user saves and retrieves a draft message verify it has a DRAFT label
    Given new sending from internal to respondent
      And   new the message is saved as draft
    When  new the message is read
    Then a success status code (200) is returned
      And new the response message has the label 'DRAFT'

  Scenario Outline: Respondent saves and retrieves a draft message verify the message fields are as sent
    Given new sending from respondent to internal
      And   new the message is saved as draft
    When  new the message is read
    Then a success status code (200) is returned
      And new retrieved message <field> is as was saved

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
    Given new sending from internal to respondent
      And   new the message is saved as draft
    When  new the message is read
    Then a success status code (200) is returned
      And new retrieved message <field> is as was saved

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
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message with id '12345678-ed43-4cdb-ad1c-450f9986859b' is retrieved
    Then  a not found status code (404) is returned

  Scenario: Internal user retrieves a message with incorrect message ID
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the message with id '12345678-ed43-4cdb-ad1c-450f9986859b' is retrieved
    Then  a not found status code (404) is returned

  Scenario: Respondent sends message and retrieves the same message with it's labels
    Given new sending from respondent to internal
      And   new the message is sent
    When  new the message is read
    Then  new the response message has the label 'SENT'

  Scenario: Internal user sends message and retrieves the same message with it's labels
    Given new sending from internal to respondent
    When  new the message is sent
      And   new the message is read
    Then  new the response message has the label 'SENT'

Scenario: Respondent sends message and internal user retrieves the same message with it's labels
  Given   new sending from respondent to internal
      And   new the message is sent
    When  new the user is set as internal
      And   new the message is read
    Then  new the response message has the label 'INBOX'
      And   new the response message has the label 'UNREAD'
      And   new the response message should a label count of '2'

  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
    Given new sending from internal to respondent
      And   new the message is sent
    When  new the user is set as respondent
      And   new the message is read
    Then  new the response message has the label 'INBOX'
      And   new the response message has the label 'UNREAD'
      And   new the response message should a label count of '2'

  Scenario: Respondent attempts to read a message they did not send or receive
    Given new sending from respondent to internal
    When  new the message is sent
      And   new the user is set as alternative respondent
      And   new the message is read
    Then a forbidden status code (403) is returned








