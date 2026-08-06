import re
import time
from pathlib import Path

_ROOT = Path(__file__).parent.parent
SCREENSHOT_DIR = _ROOT / "screenshots"


def _sanitize(name: str) -> str:
    """Turn an arbitrary step/scenario name into a safe filename stem."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "screenshot"


def capture_screenshot(driver, name: str = "screenshot") -> str | None:
    """Save a screenshot of the current screen to ``screenshots/``.

    Returns the file path on success, or ``None`` when the capture fails so
    that screenshotting never breaks a test run.
    """
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        stem = f"{_sanitize(name)}_{time.strftime('%Y%m%d_%H%M%S')}"
        path = SCREENSHOT_DIR / f"{stem}.png"
        counter = 1
        while path.exists():
            path = SCREENSHOT_DIR / f"{stem}_{counter}.png"
            counter += 1
        return str(path) if driver.save_screenshot(str(path)) else None
    except Exception:
        return None
