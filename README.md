# Appium Mobile Test Framework

Python · pytest · pytest-bdd · Appium — supports **Android** and **iOS**.

---

## Project structure

```
appium-framework/
├── .github/workflows/       # GitHub Actions CI pipelines
├── apps/                    # Drop .apk / .ipa files here (git-ignored)
├── config/
│   ├── capabilities.yaml    # Appium capabilities per platform
│   ├── devices.yaml         # Device / emulator UDIDs
│   └── users.yaml           # Test user credentials
├── features/                # Gherkin feature files
├── pages/
│   ├── base_page.py         # All shared mobile interactions
│   ├── login_page.py
│   └── home_page.py
├── step_defs/               # pytest-bdd step definitions & test entry points
├── utils/
│   ├── config_loader.py     # YAML loaders
│   ├── driver_factory.py    # Appium driver builder
│   ├── reporting.py         # Session report + per-case log files
│   └── screenshot.py        # Per-step screenshot capture
└── conftest.py              # Session-level fixtures (driver)
```

---

## Quick start

### 1 — Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| [uv](https://docs.astral.sh/uv/) | latest |
| Node.js | ≥ 18 |
| Appium | ≥ 2.x (`npm i -g appium`) |
| Appium driver | `appium driver install uiautomator2` (Android) |
| | `appium driver install xcuitest` (iOS) |

### 2 — Install dependencies

```bash
uv sync
```

### 3 — Configure your app

Edit the YAML files under `config/`:

**`config/capabilities.yaml`** — set `app_package` / `app_activity` (Android) or `bundle_id` (iOS).

**`config/devices.yaml`** — paste your device or emulator UDID.

**`config/users.yaml`** — add test account credentials.

> **Tip:** copy `config/users.yaml` to `config/users.local.yaml` for secrets — the local file is git-ignored.

### 4 — Start Appium

```bash
appium
```

### 5 — Run tests

```bash
# Android (default)
uv run pytest step_defs/ -v

# iOS
uv run pytest step_defs/ --platform ios -v

# Target a specific device key
uv run pytest step_defs/ --platform android --device-key real_device -v

# Generate HTML report
uv run pytest step_defs/ --html=reports/report.html --self-contained-html
```

---

## Adding a new screen

1. Create `pages/my_page.py` — extend `BasePage`.
2. Add locators in `_ANDROID` / `_IOS` dicts at the top of the file.
3. Write a `features/my_screen.feature` file.
4. Create `step_defs/test_my_screen.py` with `scenarios("../features/my_screen.feature")` and step functions.

---

## Screenshots

A screenshot is taken automatically after **every step** in each scenario (and when a step fails), so you get one image per Gherkin step without touching any step definition.

- Files are saved to `screenshots/` as `<scenario>_L<line>_<given|when|then>_<step text>_<timestamp>.png`.
- Manual captures are still available via `BasePage.take_screenshot(name)`.

---

## Reporting & logs

Every session writes its artefacts to a timestamped folder `reports/run_<timestamp>/`:

| File | Content |
|------|---------|
| `session_report.json` | Pass/fail record of every case — name, feature/scenario, outcome, duration, error text |
| `logs/<case>.log` | One log file per case — step-by-step flow, driver lifecycle, full traceback on failure |

A short summary (counts + file locations) is also printed at the end of every run.

---

## `BasePage` reference

| Method | Description |
|--------|-------------|
| `click(locator)` | Wait then tap an element |
| `raw_click(x, y)` | Tap at absolute screen coordinates |
| `send_keys(locator, text)` | Clear then type into a field |
| `scroll_down()` / `scroll_up()` | Full-page swipe gesture |
| `scroll_to_element(locator)` | Scroll until element is visible |
| `scroll_down_in_element(locator)` | Scroll inside a container |
| `wait_for_element(locator)` | Wait until visible, return element |
| `is_element_present(locator)` | Non-throwing existence check |
| `is_element_visible(locator)` | Non-throwing visibility check |
| `handle_wheel_picker(locator, value)` | Select value in drum-roll / wheel picker |
| `hide_keyboard()` | Dismiss the on-screen keyboard |
| `take_screenshot(name)` | Save screenshot to `screenshots/` |

---

## CI / CD

| Workflow | Trigger | Runner |
|----------|---------|--------|
| `android-tests.yml` | push / PR / manual | `ubuntu-latest` |
| `ios-tests.yml` | push / PR / manual | `macos-latest` |

Both workflows accept a `device_key` input for manual runs so you can target a specific device profile without changing code.
