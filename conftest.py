import os
import pytest
from utils.driver_factory import create_driver


def pytest_addoption(parser):
    parser.addoption("--platform", action="store", default=None, help="Target platform: android | ios")
    parser.addoption("--device-key", action="store", default=None, help="Key from devices.yaml (e.g. emulator, real_device)")


@pytest.fixture(scope="session")
def platform(request) -> str:
    return request.config.getoption("--platform") or os.environ.get("PLATFORM", "android")


@pytest.fixture(scope="session")
def device_key(request) -> str:
    return request.config.getoption("--device-key") or os.environ.get("DEVICE_KEY")


@pytest.fixture(scope="function")
def driver(platform, device_key):
    """Create an Appium driver for each test function and quit it after."""
    _driver = create_driver(platform=platform, device_key=device_key)
    yield _driver
    _driver.quit()
