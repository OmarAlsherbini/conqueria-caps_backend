Feature: Attack Unit Management

  Scenario: Creating an attack unit
    Given a new attack unit with the following attributes:
      | name            | Air Fighter          |
      | picture         | air_fighter.png      |
      | cost            | 1000                 |
      | health_points   | 500                  |
      | damage          | 50                   |
      | speed           | 2.5                  |
      | accuracy        | 0.85                 |
      | max_number_per_line | 10               |
      | is_air          | true                 |
      | is_sea          | false                |
      | turns_to_build  | 3                    |
      | experience_value| 150                  |
      | shop_cost       | 50                   |
      | rarity          | rare                 |
      | description     | A fast air unit      |
    When the attack unit is created
    Then the attack unit should be stored in the database
    
  Scenario: Create a new Attack Unit
    Given I have valid attributes for an Attack Unit
    When I create a new Attack Unit
    Then the Attack Unit should be saved in the database with correct attributes

  Scenario: Retrieve an existing Attack Unit
    Given an Attack Unit exists in the database
    When I retrieve the Attack Unit by ID
    Then I should receive the correct Attack Unit details

  Scenario: Update an Attack Unit
    Given an Attack Unit exists in the database
    When I update the Attack Unit's attributes
    Then the changes should be reflected in the database

  Scenario: Delete an Attack Unit
    Given an Attack Unit exists in the database
    When I delete the Attack Unit
    Then the Attack Unit should no longer exist in the database

