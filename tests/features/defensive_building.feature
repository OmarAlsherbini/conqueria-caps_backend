Feature: Defensive Building Management

  Scenario: Creating a defensive building
    Given a new defensive building with the following attributes:
      | name            | Anti-Air Turret      |
      | damage          | 100                  |
      | range           | 50                   |
      | fire_rate       | 2                    |
      | can_attack_air  | true                 |
      | accuracy        | 0.9                  |
      | attack_sound    | air_turret_shot.mp3  |
      | mode            | Single-target        |
      | damage_radius   |                      |
      | level           | 1                    |
    When the defensive building is created
    Then the defensive building should be stored in the database

  Scenario: Create a new Defensive Building
    Given I have valid attributes for a Defensive Building
    When I create a new Defensive Building
    Then the Defensive Building should be saved in the database with correct attributes

  Scenario: Retrieve an existing Defensive Building
    Given a Defensive Building exists in the database
    When I retrieve the Defensive Building by ID
    Then I should receive the correct Defensive Building details

  Scenario: Update a Defensive Building
    Given a Defensive Building exists in the database
    When I update the Defensive Building's attributes
    Then the changes should be reflected in the database

  Scenario: Delete a Defensive Building
    Given a Defensive Building exists in the database
    When I delete the Defensive Building
    Then the Defensive Building should no longer exist in the database
