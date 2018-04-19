Feature: Message get by ID Endpoint V2

  Background: Reset database
    Given prepare for tests using 'mock' services

  Scenario Outline: Respondent saves and retrieves a message verify the message fields are as sent
    Given sending from respondent to internal <user>
      And   the message is sent V2
      And the message is read V2
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

   Examples: Fields, user
    |field                |user          |
    |msg_to               |specific user |
    |msg_from             |specific user |
    |body                 |specific user |
    |subject              |specific user |
    |ru                   |specific user |
    |Collection Case      |specific user |
    |Collection Exercise  |specific user |
    |survey               |specific user |
    |msg_to               |group         |
    |msg_from             |group         |
    |body                 |group         |
    |subject              |group         |
    |ru                   |group         |
    |Collection Case      |group         |
    |Collection Exercise  |group         |
    |survey               |group         |


  Scenario Outline: Internal user saves and retrieves a message verify the message fields are as sent
    Given sending from internal <user> to respondent
      And   the message is sent V2
      And the message is read V2
    Then a success status code (200) is returned
      And retrieved message <field> is as was saved

   Examples: Fields, user
    |field                |user          |
    |msg_to               |specific user |
    |msg_from             |specific user |
    |body                 |specific user |
    |subject              |specific user |
    |ru                   |specific user |
    |Collection Case      |specific user |
    |Collection Exercise  |specific user |
    |survey               |specific user |
    |msg_to               |group         |
    |msg_from             |group         |
    |body                 |group         |
    |subject              |group         |
    |ru                   |group         |
    |Collection Case      |group         |
    |Collection Exercise  |group         |
    |survey               |group         |

  Scenario: Respondent saves a message to GROUP and retrieves it verify the @msg_to is correctly populated
    Given sending from respondent to internal group
      And   the message is sent V2
      And the message is read V2
    Then a success status code (200) is returned
      And the at_msg_to is set correctly for internal group

  Scenario: Respondent saves a message to BRES and retrieves itge verify the @msg_to is correctly populated
    Given sending from respondent to internal user
      And   the message is sent
      And the message is read V2
    Then a success status code (200) is returned
      And the at_msg_to is set correctly for internal user