Feature: Get threads list Endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: There are 3 conversations between respondent and internal , respondent attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent V2
      And the message is sent V2
      And the message is sent V2
   When the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between respondent and internal , internal attempts to read them
    Given sending from respondent to internal <user>
      And '3' messages are sent using V2
     When   the user is set as internal <user>
      And the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between respondent and internal each with 2 messages, respondent attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

      And   the thread_id is set to empty
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

      And   the thread_id is set to empty
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

   When the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between respondent and internal each with 2 messages, internal user attempts to read them
    Given sending from respondent to internal <user>
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

      And   the thread_id is set to empty
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

      And   the thread_id is set to empty
      And the message is sent V2
      And   the thread id is set to the last returned thread id
      And the message is sent V2

    When  the user is set as internal <user>
      And the threads are read
    Then  a success status code (200) is returned
      And '3' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between respondent and internal each with 2  messages and a draft, validate most recent message returned for each
    Given sending from respondent to internal <user>
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

      And the thread_id is set to empty
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

      And the thread_id is set to empty
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

   When the threads are read
    Then  a success status code (200) is returned
      And  '3' messages are returned
          # Drafts added last
      And '3' messages have a 'DRAFT' label

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages and a draft, validate most recent message returned for each
    Given sending from internal <user> to respondent
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

      And the thread_id is set to empty
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

      And the thread_id is set to empty
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is saved as draft V2

   When the threads are read
    Then  a success status code (200) is returned
      And  '3' messages are returned
      # Drafts added last
      And '3' messages have a 'DRAFT' label

    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different survey_id validate , that only 2 messages returned when we restrict by survey

    Given sending from internal <user> to respondent
      And the survey is set to 'Survey1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the survey is set to 'Survey2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the survey is set to 'Survey1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

    When the threads in survey 'Survey1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different survey_id validate , that only 2 messages returned when we restrict by survey

    Given sending from respondent to internal <user>
      And the survey is set to 'Survey1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the survey is set to 'Survey2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the survey is set to 'Survey1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

    When the threads in survey 'Survey1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different ru validate , that only 2 messages returned when we restrict by ru

    Given sending from internal <user> to respondent
      And the ru is set to 'ru1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the ru is set to 'ru2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the ru is set to 'ru1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

    When the threads with ru 'ru1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different ru validate , that only 2 messages returned when we restrict by ru

    Given sending from respondent to internal <user>
      And the ru is set to 'ru1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the ru is set to 'ru2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the ru is set to 'ru1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

    When the threads with ru 'ru1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |

  Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different collection case validate , that only 2 messages returned when we restrict by collection case

    Given sending from internal <user> to respondent
      And the collection case is set to 'col1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection case is set to 'col2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection case is set to 'col1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
    When the threads with collection case 'col1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different collection case validate , that only 2 messages returned when we restrict by collection case

    Given sending from respondent to internal <user>
      And the collection case is set to 'col1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection case is set to 'col2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection case is set to 'col1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

    When the threads with collection case 'col1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


 Scenario Outline: There are 3 conversations between an internal user and respondent each with 2  messages ,
                    each with different collection exercise validate , that only 2 messages returned when we restrict by collection exercise

    Given sending from internal <user> to respondent
      And the collection_exercise is set to 'ce1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
    When the threads with collection exercise 'ce1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There are 3 conversations between an respondent and internal user each with 2  messages ,
                    each with different collection exercise validate , that only 2 messages returned when we restrict by collection exercise

    Given sending from respondent to internal <user>
      And the collection_exercise is set to 'ce1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce2'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2

      And the thread_id is set to empty
      And the collection_exercise is set to 'ce1'
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the message is sent V2
    When the threads with collection exercise 'ce1' are read
    Then  a success status code (200) is returned
      And  '2' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |


 Scenario Outline: A respondent sends a very long message, the internal user sees a 100 character summary in their inbox
    Given sending from internal <user> to respondent
      And the message body is '5000' characters long
      And '1' messages are sent using V2
    When the threads are read
    Then the message bodies are 100 characters or less


  Scenario Outline: There is a conversation between respondent and internal the last message is a draft with an empty to field ,
                    respondent attempts to read them, should receive  a 200
    Given sending from respondent to internal <user>
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the to is set to empty
      And the message is saved as draft V2
   When the threads are read
    Then  a success status code (200) is returned
      And '1' messages are returned

    Examples: user type
    | user        |
    | specific user |
    | group        |


  Scenario Outline: There is a conversation between internal and respondent the last message is a draft with an empty to field ,
                    respondent attempts to read them, should receive  a 200
    Given sending from internal <user> to respondent
      And the message is sent V2
      And the thread id is set to the last returned thread id
      And the to is set to empty
      And the message is saved as draft V2
   When the threads are read
    Then  a success status code (200) is returned
      And '1' messages are returned


    Examples: user type
    | user        |
    | specific user |
    | group        |
    | group        |
