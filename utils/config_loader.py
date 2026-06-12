import os
import yaml
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_CONFIG_DIR = _ROOT / "config"


def _load(filename: str) -> dict:
    path = _CONFIG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_users() -> dict:
    return _load("users.yaml")["users"]


def get_user(role: str = "default") -> dict:
    return get_users()[role]


def get_devices(platform: str) -> dict:
    """Return all device entries for a platform ('android' or 'ios')."""
    return _load("devices.yaml")[platform]


def get_device(platform: str, device_key: str = None) -> dict:
    """Return a single device config.

    Falls back to the first device in the platform block when device_key is
    not provided — handy for local runs where only one device is connected.
    """
    devices = get_devices(platform)
    if device_key:
        return devices[device_key]
    # Honour the DEVICE_KEY env var so CI can pin a specific device.
    env_key = os.environ.get("DEVICE_KEY")
    if env_key and env_key in devices:
        return devices[env_key]
    return next(iter(devices.values()))


def get_capabilities(platform: str) -> dict:
    data = _load("capabilities.yaml")
    return {
        "server_url": data["appium_server"]["url"],
        **data[platform],
    }
