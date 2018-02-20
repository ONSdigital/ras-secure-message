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



