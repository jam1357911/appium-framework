import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.config_loader import get_user

scenarios("../features/home.feature")


# ------------------------------------------------------------------
# Background
# ------------------------------------------------------------------

@given("the user is logged in")
def user_is_logged_in(driver):
    user = get_user("default")
    LoginPage(driver).login(user["username"], user["password"])


# ------------------------------------------------------------------
# Then
# ------------------------------------------------------------------

@then("the home page is displayed")
def assert_home_displayed(driver):
    assert HomePage(driver).is_home_page_displayed()


@then("the welcome text is visible")
def assert_welcome_visible(driver):
    text = HomePage(driver).get_welcome_text()
    assert text, "Welcome text was empty"


# ------------------------------------------------------------------
# Scroll
# ------------------------------------------------------------------

@when("the user scrolls down the item list")
def scroll_item_list(driver):
    HomePage(driver).scroll_item_list_down()


@then("the item list is still visible")
def item_list_visible(driver):
    assert HomePage(driver).is_element_visible(HomePage(driver)._loc["item_list"])


# ------------------------------------------------------------------
# Wheel picker
# ------------------------------------------------------------------

@when(parsers.parse('the user selects month "{month}" from the date picker'))
def select_month(driver, month):
    HomePage(driver).select_month(month)


@when(parsers.parse('the user selects year "{year}" from the date picker'))
def select_year(driver, year):
    HomePage(driver).select_year(year)


@then("the selected date is reflected on screen")
def date_reflected(driver):
    # Replace with a real assertion against the displayed date label.
    assert HomePage(driver).is_element_visible(HomePage(driver)._loc["date_picker"])


# ------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------

@when("the user taps logout")
def tap_logout(driver):
    HomePage(driver).tap_logout()


@then("the login page is displayed")
def assert_login_page(driver):
    assert LoginPage(driver).is_login_page_displayed()
