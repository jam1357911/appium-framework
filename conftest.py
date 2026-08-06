import os
import pytest
from utils.driver_factory import create_driver
from utils.screenshot import capture_screenshot


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


# ------------------------------------------------------------------
# Per-step screenshots
# ------------------------------------------------------------------

_MAX_SCREENSHOT_NAME_LEN = 100


def _step_screenshot_name(scenario, step) -> str:
    name = f"{scenario.name}_L{step.line_number}_{step.type}_{step.name}"
    return name[:_MAX_SCREENSHOT_NAME_LEN]


def _take_step_screenshot(request, scenario, step):
    try:
        _driver = request.getfixturevalue("driver")
    except Exception:
        return
    capture_screenshot(_driver, _step_screenshot_name(scenario, step))


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """Capture a screenshot after every successfully executed step."""
    _take_step_screenshot(request, scenario, step)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Capture a screenshot when a step fails."""
    _take_step_screenshot(request, scenario, step)
