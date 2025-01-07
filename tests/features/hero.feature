Feature: Hero Management

  Scenario: Creating a hero
    Given a new hero with the following attributes:
      | name            | General Blitz        |
      | rarity          | Legendary            |
      | civ             | Roman                |
      | role            | Commander            |
      | picture         | general_blitz.png    |
      | description     | A swift and aggressive hero |
      | catch_phrase    | "Strike fast, strike hard!" |
      | bonus_description | Boosts troop speed by 10% |
      | shop_cost       | 500                  |
    When the hero is created
    Then the hero should be stored in the database

  Scenario: Create a new Hero
    Given I have valid attributes for a Hero
    When I create a new Hero
    Then the Hero should be saved in the database with correct attributes

  Scenario: Retrieve an existing Hero
    Given a Hero exists in the database
    When I retrieve the Hero by ID
    Then I should receive the correct Hero details

  Scenario: Update a Hero
    Given a Hero exists in the database
    When I update the Hero's attributes
    Then the changes should be reflected in the database

  Scenario: Delete a Hero
    Given a Hero exists in the database
    When I delete the Hero
    Then the Hero should no longer exist in the database
