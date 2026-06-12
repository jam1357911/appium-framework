Feature: Login

  Background:
    Given the app is launched

  Scenario: Successful login with valid credentials
    When the user enters username "test_user@example.com" and password "Test@1234"
    And the user taps the login button
    Then the home page is displayed

  Scenario: Login fails with invalid credentials
    When the user enters username "wrong@example.com" and password "wrongpass"
    And the user taps the login button
    Then an error message is displayed

  Scenario Outline: Login with different user roles
    When the user logs in as "<role>"
    Then the home page is displayed

    Examples:
      | role    |
      | default |
      | admin   |
