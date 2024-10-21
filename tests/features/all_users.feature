Feature: Fetch all users with pagination

  Scenario: Fetch the first set of users
    Given there are registered users in the system
    When I request the first page of users
    Then I should receive a list of users
    And the list should be paginated
    And I should see the cursor for the next set of users

  Scenario: Fetch the next set of users
    Given I have the cursor from the first page
    When I request the next set of users using the cursor
    Then I should receive the next set of users
    And the list should be paginated
    And I should see the cursor for the next set of users
