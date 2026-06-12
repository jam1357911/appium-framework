Feature: Home screen

  Background:
    Given the user is logged in

  Scenario: Home screen displays welcome message
    Then the home page is displayed
    And the welcome text is visible

  Scenario: User can scroll the item list
    When the user scrolls down the item list
    Then the item list is still visible

  Scenario: User selects a date from the wheel picker
    When the user selects month "June" from the date picker
    And the user selects year "2025" from the date picker
    Then the selected date is reflected on screen

  Scenario: User can log out
    When the user taps logout
    Then the login page is displayed
