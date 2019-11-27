Feature: Get threads list Endpoint

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And the message is sent
      And the message is sent
   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal specific user
      And '3' messages are sent
     When   the user is set as internal
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given sending from respondent to internal specific user
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

    When  the user is set as internal
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

  Scenario: A respondent sends a very long message, the internal user sees a 100 character summary in their inbox
    Given sending from internal specific user to respondent
      And the message body is '5000' characters long
      And '1' messages are sent
    When the threads are read
    Then the message bodies are '100' characters or less

  Scenario: There are 50 conversations between respondent and internal user. Internal user gets conversations should see 50
   Given sending from respondent to internal group
    And '50' messages are sent
   When the user is set as internal specific user
    And the threads are read
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 conversations between internal user and respondent. Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent
   When the user is set as respondent
    And the threads are read
   Then  '50' messages have a 'INBOX' label

  Scenario: There are 50 conversations between internal user and respondent. Alternative Internal user gets conversations should see 50
   Given sending from internal specific user to respondent
    And '50' messages are sent
   When the user is set to alternative internal specific user
    And the threads are read
   Then  '50' messages have a 'SENT' label

  Scenario: The respondent attempts to get conversation list with my_conversations argument set. 400 should be returned
    Given the user is set as respondent
    When  the threads are read with my_conversations set true
    Then a bad request status code 400 is returned

  Scenario: There are 10 conversations each from 2 internal users. Internal user gets threads using my conversations, they only see theirs
    Given  sending from internal specific user to respondent
     And  '10' messages are sent
     And  sending from alternate internal specific user to respondent
     And '9' messages are sent
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '9' messages are returned
     And  all messages are from alternate internal specific user

  Scenario: Two internal users in a conversation with a respondent, with my_conversations set true then the last one will see it in conversation list
    Given sending from respondent to internal specific user
      And the message is sent
      And sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And sending from alternate internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '1' messages are returned
     And  all messages are from alternate internal specific user

  Scenario: Two internal users in a conversation with a respondent, with my_conversations set true then the first  one will NOT see it in conversation list
    Given sending from respondent to internal specific user
      And the message is sent
      And sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And sending from alternate internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the user is set as internal specific user
    When  the threads are read with my_conversations set true
    Then  a success status code 200 is returned
     And '0' messages are returned

  Scenario: Respondent sends to Group , internal user should not see them in threads when using my_conversations
      Given sending from respondent to internal group
        And the message is sent
      When  the user is set as internal specific user
        And the threads are read with my_conversations set true
      Then  '0' messages are returned

Scenario Outline: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent
      And the message is sent
      And the message is sent
   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal <user>
      And '3' messages are sent
     When   the user is set as internal <user>
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

   When the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

      And   the thread_id is set to empty
      And the message is sent
      And   the thread id is set to the last returned thread id
      And the message is sent

    When  the user is set as internal <user>
      And the threads are read
    Then  a success status code 200 is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different survey_id validate , that only 2 messages returned when we restrict by survey

    Given sending from internal <user> to respondent
      And the survey is set to 'Survey1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the survey is set to 'Survey2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the survey is set to 'Survey1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

    When the threads in survey 'Survey1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different survey_id validate , that only 2 messages returned when we restrict by survey

    Given sending from respondent to internal <user>
      And the survey is set to 'additional_survey_1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the survey is set to 'additional_survey_2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the survey is set to 'additional_survey_1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

    When the threads in survey 'additional_survey_1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2 messages,
                    each with different business_ids, Validate that only 2 messages returned when we restrict by business_id

    Given sending from internal <user> to respondent
      And the business_id is set to 'ru1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the business_id is set to 'ru2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the business_id is set to 'ru1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

    When the threads with business_id 'ru1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2 messages,
                    each with different business_ids. Validate that only 2 messages returned when we restrict by business_id

    Given sending from respondent to internal <user>
      And the business_id is set to 'additional_ru1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the business_id is set to 'additional_ru2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the business_id is set to 'additional_ru1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

    When the threads with business_id 'additional_ru1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different collection case validate , that only 2 messages returned when we restrict by collection case

    Given sending from internal <user> to respondent
      And the collection case is set to 'col1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection case is set to 'col2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection case is set to 'col1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
    When the threads with collection case 'col1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different collection case validate , that only 2 messages returned when we restrict by collection case

    Given sending from respondent to internal <user>
      And the collection case is set to 'col1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection case is set to 'col2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection case is set to 'col1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

    When the threads with collection case 'col1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


 Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different collection exercise validate , that only 2 messages returned when we restrict by collection exercise

    Given sending from internal <user> to respondent
      And the collection_exercise is set to 'ce1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
    When the threads with collection exercise 'ce1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different collection exercise validate , that only 2 messages returned when we restrict by collection exercise

    Given sending from respondent to internal <user>
      And the collection_exercise is set to 'ce1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce2'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce1'
      And the message is sent
      And the thread id is set to the last returned thread id
      And the message is sent
    When the threads with collection exercise 'ce1' are read
    Then  a success status code 200 is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


 Scenario: A respondent sends a very long message, the internal user sees a 100 character summary in their inbox
    Given sending from respondent to internal group
      And the message body is '5000' characters long
      And '1' messages are sent
    When the threads are read
    Then the message bodies are '100' characters or less


  Scenario: There is a conversation between internal user and respondent, the last message being a message sent from
              Internal to tests/behavioural/features/threads_get.feature:425respondent. A second internal person reads the conversation, they should see the message
              sent from internal to respondent
    Given sending from respondent to internal group
      And the message is sent
      And sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the user is set to alternative internal specific user
    When the threads are read
    Then  a success status code 200 is returned
      And  '1' messages are returned
      And all response messages have the label 'SENT'

  Scenario: An internal user sends messages regarding multiple different surveys, validate that when the get the threads list
            filtered by both surveys then all messages are returned
    Given sending from internal specific user to respondent
      And survey set to default survey
      And the message is sent
      And sending from internal specific user to respondent
      And survey is set to alternate survey
      And the message is sent
      And the user is set as internal specific user
    When the threads in are read with filters for both default and alternate surveys
    Then  a success status code 200 is returned
      And  '2' messages are returned

  Scenario: A respondent sends messages regarding multiple different surveys, validate that when the get the threads list
        filtered by both surveys then all messages are returned
    Given sending from respondent to internal group
      And survey set to default survey
      And the message is sent
      And sending from respondent to internal group
      And survey is set to alternate survey
      And the message is sent
      And the user is set as internal specific user
    When the threads in are read with filters for both default and alternate surveys
    Then  a success status code 200 is returned
      And  '2' messages are returned

  Scenario:Respondent tries to retrieve a conversation that they are not part of via thread id
    Given sending from respondent to internal specific user
      And   the message is sent
      And   the thread id is set to the last returned thread id
    When the user is set as alternative respondent
     And  the thread is read
    Then  a forbidden status code 403 is returned

  Scenario: Internal user looks for new respondent message when one exists
    Given sending from respondent to internal group
    And the message is sent
    When the user is set as internal specific user
    And the threads are read with new_respondent_conversations set true
    Then  '1' messages are returned

  Scenario: Internal user looks for new respondent message when last message was replied to exists
    Given sending from respondent to internal group
      And the message is sent
    When sending from internal specific user to respondent
      And the thread id is set to the last returned thread id
      And the message is sent
      And the threads are read with new_respondent_conversations set true
    Then  '0' messages are returned

  Scenario: Respondent attempts to filter by new respondent message
    Given the user is set as respondent
    When the threads are read with new_respondent_conversations set true
    Then a bad request status code 400 is returned

  Scenario: Internal user starts a conversation and then looks for new_respondent_conversations
    Given sending from internal specific user to respondent
      And the message is sent
    When the threads are read with new_respondent_conversations set true
    Then  '0' messages are returned
