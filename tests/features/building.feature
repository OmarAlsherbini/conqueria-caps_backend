Feature: Building Management

  Scenario: Creating a building
    Given a new building with the following attributes:
      | name            | Fortress             |
      | type            | Defensive            |
      | picture         | fortress.png         |
      | health_points   | 1000                 |
      | cost            | 2000                 |
      | turns_to_build  | 5                    |
      | experience      | 0                    |
      | upgrade_threshold | 500                |
      | shop_cost       | 100                  |
      | rarity          | legendary            |
      | description     | A strong defensive structure |
    When the building is created
    Then the building should be stored in the database

  Scenario: Create a new Building
    Given I have valid attributes for a Building
    When I create a new Building
    Then the Building should be saved in the database with correct attributes

  Scenario: Retrieve an existing Building
    Given a Building exists in the database
    When I retrieve the Building by ID
    Then I should receive the correct Building details

  Scenario: Update a Building
    Given a Building exists in the database
    When I update the Building's attributes
    Then the changes should be reflected in the database

  Scenario: Delete a Building
    Given a Building exists in the database
    When I delete the Building
    Then the Building should no longer exist in the database
