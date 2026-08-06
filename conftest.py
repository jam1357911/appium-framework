import os

import pytest

from utils import reporting
from utils.driver_factory import create_driver
from utils.screenshot import capture_screenshot

logger = reporting.get_logger()


def pytest_addoption(parser):
    parser.addoption("--platform", action="store", default=None, help="Target platform: android | ios")
    parser.addoption("--device-key", action="store", default=None, help="Key from devices.yaml (e.g. emulator, real_device)")


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    if session.config.option.collectonly:
        return
    reporting.start_run()


@pytest.fixture(scope="session")
def platform(request) -> str:
    return request.config.getoption("--platform") or os.environ.get("PLATFORM", "android")


@pytest.fixture(scope="session")
def device_key(request) -> str:
    return request.config.getoption("--device-key") or os.environ.get("DEVICE_KEY")


@pytest.fixture(scope="function")
def driver(platform, device_key):
    """Create an Appium driver for each test function and quit it after."""
    logger.info("Creating Appium driver (platform=%s, device_key=%s)", platform, device_key)
    _driver = create_driver(platform=platform, device_key=device_key)
    logger.info("Appium session started")
    yield _driver
    logger.info("Quitting Appium driver")
    _driver.quit()


# ------------------------------------------------------------------
# Session report & per-case logs
# ------------------------------------------------------------------

def pytest_runtest_setup(item):
    run = reporting.current_run()
    if run is None:
        return
    feature, scenario = reporting.parse_feature_scenario(item)
    run.register_case(item.nodeid, item.name, feature, scenario)
    run.open_case_log(reporting.case_label(item))
    logger.info("=== Case started: %s ===", item.name)
    logger.info("Node ID: %s", item.nodeid)
    if feature or scenario:
        logger.info("Feature: %s | Scenario: %s", feature, scenario)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    run = reporting.current_run()
    result = run.result_for(item.nodeid) if run else None
    if report.when == "setup":
        if report.failed:
            if result:
                result.outcome = "error"
                result.error = report.longreprtext
            logger.error("Setup failed:\n%s", report.longreprtext)
    elif report.when == "call":
        if result:
            result.duration = report.duration
            if report.failed:
                result.outcome = "failed"
                result.error = report.longreprtext
            elif report.skipped:
                result.outcome = "skipped"
            else:
                result.outcome = "passed"
        if report.failed:
            logger.error("Case FAILED:\n%s", report.longreprtext)
        elif report.skipped:
            logger.warning("Case skipped")
        else:
            logger.info("Case PASSED (%.2fs)", report.duration)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    yield
    run = reporting.current_run()
    if run is None:
        return
    result = run.result_for(item.nodeid)
    if result:
        logger.info(
            "=== Case finished: %s | outcome=%s | duration=%.2fs ===",
            result.name,
            result.outcome,
            result.duration,
        )
    run.close_case_log()


def pytest_sessionfinish(session, exitstatus):
    run = reporting.current_run()
    if run is None or not run.results:
        return
    platform = session.config.getoption("--platform") or os.environ.get("PLATFORM", "android")
    run.write_report(exitstatus, platform)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    run = reporting.current_run()
    if run is None or run.report_path is None:
        return
    counts = run.counts()
    terminalreporter.write_sep("-", "session report")
    terminalreporter.write_line(
        f"total={counts['total']} passed={counts['passed']} failed={counts['failed']} "
        f"error={counts['error']} skipped={counts['skipped']}"
    )
    terminalreporter.write_line(f"Report: {run.report_path}")
    terminalreporter.write_line(f"Per-case logs: {run.logs_dir}")


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


def pytest_bdd_before_step_call(request, feature, scenario, step, step_func, step_func_args):
    logger.info("Step start: %s %s", step.type, step.name)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """Capture a screenshot after every successfully executed step."""
    logger.info("Step passed: %s %s", step.type, step.name)
    _take_step_screenshot(request, scenario, step)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Capture a screenshot when a step fails."""
    logger.error("Step failed: %s %s -> %r", step.type, step.name, exception)
    _take_step_screenshot(request, scenario, step)
