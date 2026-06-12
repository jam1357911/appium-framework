import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.config_loader import get_user

scenarios("../features/login.feature")


# ------------------------------------------------------------------
# Background
# ------------------------------------------------------------------

@given("the app is launched")
def app_is_launched(driver):
    # The driver fixture already launches the app; nothing extra needed.
    pass


# ------------------------------------------------------------------
# When
# ------------------------------------------------------------------

@when(parsers.parse('the user enters username "{username}" and password "{password}"'))
def enter_credentials(driver, username, password):
    LoginPage(driver).enter_username(username)
    LoginPage(driver).enter_password(password)


@when("the user taps the login button")
def tap_login(driver):
    LoginPage(driver).tap_login()


@when(parsers.parse('the user logs in as "{role}"'))
def login_as_role(driver, role):
    user = get_user(role)
    LoginPage(driver).login(user["username"], user["password"])


# ------------------------------------------------------------------
# Then
# ------------------------------------------------------------------

@then("the home page is displayed")
def home_page_displayed(driver):
    assert HomePage(driver).is_home_page_displayed(), "Home page was not displayed after login"


@then("an error message is displayed")
def error_message_displayed(driver):
    assert LoginPage(driver).is_error_displayed(), "Expected an error message but none was shown"
