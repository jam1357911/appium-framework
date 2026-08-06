import os
from appium import webdriver
from appium.options.common.base import AppiumOptions
from utils.config_loader import get_capabilities, get_device


def create_driver(platform: str = None, device_key: str = None) -> webdriver.Remote:
    """Build and return an Appium RemoteWebDriver.

    Platform is resolved from the PLATFORM env var when not supplied — this
    lets CI pipelines set the target without touching code.
    """
    platform = (platform or os.environ.get("PLATFORM", "android")).lower()
    caps = get_capabilities(platform)
    device = get_device(platform, device_key)
    server_url = caps.pop("server_url")

    options = AppiumOptions()

    if platform == "android":
        options.platform_name = "Android"
        options.load_capabilities(
            {
                "appium:deviceName": device["device_name"],
                "appium:udid": device["udid"],
                "appium:platformVersion": device["platform_version"],
                "appium:appPackage": caps["app_package"],
                "appium:appActivity": caps["app_activity"],
                "appium:automationName": caps["automation_name"],
                "appium:noReset": caps["no_reset"],
                "appium:fullReset": caps["full_reset"],
                "appium:newCommandTimeout": caps["new_command_timeout"],
                "appium:autoGrantPermissions": caps.get("auto_grant_permissions", True),
            }
        )
        # Include app path only when the file actually exists (e.g. CI installs fresh)
        if os.path.isfile(caps.get("app_path", "")):
            options.load_capabilities({"appium:app": os.path.abspath(caps["app_path"])})

    elif platform == "ios":
        options.platform_name = "iOS"
        options.load_capabilities(
            {
                "appium:deviceName": device["device_name"],
                "appium:udid": device["udid"],
                "appium:platformVersion": device["platform_version"],
                "appium:bundleId": caps["bundle_id"],
                "appium:automationName": caps["automation_name"],
                "appium:noReset": caps["no_reset"],
                "appium:fullReset": caps["full_reset"],
                "appium:newCommandTimeout": caps["new_command_timeout"],
            }
        )
        if caps.get("xcode_org_id"):
            options.load_capabilities(
                {
                    "appium:xcodeOrgId": caps["xcode_org_id"],
                    "appium:xcodeSigningId": caps["xcode_signing_id"],
                }
            )
        if os.path.isfile(caps.get("app_path", "")):
            options.load_capabilities({"appium:app": os.path.abspath(caps["app_path"])})

    else:
        raise ValueError(f"Unsupported platform: {platform!r}. Use 'android' or 'ios'.")

    return webdriver.Remote(server_url, options=options)
