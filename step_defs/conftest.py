"""Shared pytest-bdd fixtures available to all step definition modules."""
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.config_loader import get_user


@pytest.fixture
def login_page(driver):
    return LoginPage(driver)


@pytest.fixture
def home_page(driver):
    return HomePage(driver)


@pytest.fixture
def default_user():
    return get_user("default")
