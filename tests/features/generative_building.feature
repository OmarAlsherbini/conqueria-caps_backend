Feature: Generative Building Management

  Scenario: Creating a generative building
    Given a new generative building with the following attributes:
      | name            | Gold Mine            |
      | money_per_turn  | 100                  |
      | cost            | 500                  |
      | turns_to_build  | 3                    |
      | rarity          | common               |
    When the generative building is created
    Then the generative building should be stored in the database

  Scenario: Create a new Generative Building
    Given I have valid attributes for a Generative Building
    When I create a new Generative Building
    Then the Generative Building should be saved in the database with correct attributes

  Scenario: Retrieve an existing Generative Building
    Given a Generative Building exists in the database
    When I retrieve the Generative Building by ID
    Then I should receive the correct Generative Building details

  Scenario: Update a Generative Building
    Given a Generative Building exists in the database
    When I update the Generative Building's attributes
    Then the changes should be reflected in the database

  Scenario: Delete a Generative Building
    Given a Generative Building exists in the database
    When I delete the Generative Building
    Then the Generative Building should no longer exist in the database
