import time
from typing import Optional, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Common mobile interactions shared across all page objects."""

    DEFAULT_TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver

    # ------------------------------------------------------------------
    # Waits
    # ------------------------------------------------------------------

    def wait_for_element(self, locator: Tuple[str, str], timeout: int = DEFAULT_TIMEOUT):
        """Wait until an element is visible and return it."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element not visible after {timeout}s — locator: {locator}"
            )

    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = DEFAULT_TIMEOUT):
        """Wait until an element is clickable and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_element_to_disappear(self, locator: Tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Return True once the element is gone, False if it outlasts the timeout."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Existence checks
    # ------------------------------------------------------------------

    def is_element_present(self, locator: Tuple[str, str], timeout: int = 3) -> bool:
        """Return True if the element appears within *timeout* seconds."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 3) -> bool:
        """Return True if the element is both present and visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Tap / click
    # ------------------------------------------------------------------

    def click(self, locator: Tuple[str, str], timeout: int = DEFAULT_TIMEOUT):
        """Wait for an element then tap it."""
        self.wait_for_element_clickable(locator, timeout).click()

    def raw_click(self, x: int, y: int):
        """Tap at absolute screen coordinates."""
        self.driver.execute_script("mobile: tap", {"x": x, "y": y})

    def click_element(self, element):
        """Tap a WebElement that has already been resolved."""
        element.click()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True):
        element = self.wait_for_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: Tuple[str, str]) -> str:
        return self.wait_for_element(locator).text

    # ------------------------------------------------------------------
    # Scroll
    # ------------------------------------------------------------------

    def _window_size(self) -> Tuple[int, int]:
        size = self.driver.get_window_size()
        return size["width"], size["height"]

    def scroll_down(self, swipe_fraction: float = 0.5):
        """Scroll the page downward (content moves up)."""
        w, h = self._window_size()
        start_y = int(h * 0.7)
        end_y = int(h * (0.7 - swipe_fraction))
        mid_x = w // 2
        self.driver.swipe(mid_x, start_y, mid_x, end_y, duration=600)

    def scroll_up(self, swipe_fraction: float = 0.5):
        """Scroll the page upward (content moves down)."""
        w, h = self._window_size()
        start_y = int(h * 0.3)
        end_y = int(h * (0.3 + swipe_fraction))
        mid_x = w // 2
        self.driver.swipe(mid_x, start_y, mid_x, end_y, duration=600)

    def scroll_to_element(self, locator: Tuple[str, str], max_swipes: int = 5) -> bool:
        """Keep scrolling down until the element is visible or *max_swipes* is reached."""
        for _ in range(max_swipes):
            if self.is_element_visible(locator, timeout=1):
                return True
            self.scroll_down()
        return self.is_element_visible(locator, timeout=2)

    def scroll_down_in_element(self, container_locator: Tuple[str, str]):
        """Scroll within a specific scrollable container (Android UiScrollable)."""
        # Android: delegate to UiScrollable
        if self._is_android():
            by, value = container_locator
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().{self._uiselector_from_locator(by, value)}).scrollForward()',
            )
        else:
            # iOS: fall back to a normal scroll within the element's bounding box
            el = self.wait_for_element(container_locator)
            loc = el.location
            size = el.size
            mid_x = loc["x"] + size["width"] // 2
            self.driver.swipe(
                mid_x, loc["y"] + int(size["height"] * 0.7),
                mid_x, loc["y"] + int(size["height"] * 0.3),
                duration=600,
            )

    # ------------------------------------------------------------------
    # Wheel / Picker
    # ------------------------------------------------------------------

    def handle_wheel_picker(self, picker_locator: Tuple[str, str], value: str):
        """Select *value* in a native wheel / drum-roll picker.

        Android: uses the ``mobile: selectPickerItems`` (API 26+) command which
        works with the ``android.widget.NumberPicker`` widget family.
        iOS: uses ``mobile: selectPickerWheelValue`` via XCUITest.
        """
        if self._is_android():
            self._android_select_picker(picker_locator, value)
        else:
            self._ios_select_picker(picker_locator, value)

    def _android_select_picker(self, locator: Tuple[str, str], value: str):
        element = self.wait_for_element(locator)
        try:
            # Works for NumberPicker and Spinner on Android >= 9
            self.driver.execute_script(
                "mobile: selectPickerItems",
                {"strategy": "id", "selector": locator[1], "index": 0, "item": value},
            )
        except Exception:
            # Fallback: swipe inside the picker until the desired text is visible
            self._swipe_picker_to_value(element, value)

    def _ios_select_picker(self, locator: Tuple[str, str], value: str):
        element = self.wait_for_element(locator)
        self.driver.execute_script(
            "mobile: selectPickerWheelValue",
            {"element": element, "order": "next", "offset": 0.15, "value": value},
        )

    def _swipe_picker_to_value(self, picker_element, target_value: str, max_swipes: int = 20):
        """Swipe inside a picker element until target_value is the selected item."""
        loc = picker_element.location
        size = picker_element.size
        mid_x = loc["x"] + size["width"] // 2
        center_y = loc["y"] + size["height"] // 2
        swipe_distance = int(size["height"] * 0.15)

        for _ in range(max_swipes):
            try:
                self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{target_value}")')
                return
            except NoSuchElementException:
                pass
            self.driver.swipe(mid_x, center_y + swipe_distance, mid_x, center_y - swipe_distance, duration=300)

        raise RuntimeError(f"Picker value '{target_value}' not found after {max_swipes} swipes")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_android(self) -> bool:
        return self.driver.capabilities.get("platformName", "").lower() == "android"

    @staticmethod
    def _uiselector_from_locator(by: str, value: str) -> str:
        mapping = {
            AppiumBy.ID: f'resourceId("{value}")',
            AppiumBy.XPATH: f'xpath("{value}")',
            AppiumBy.ACCESSIBILITY_ID: f'description("{value}")',
        }
        return mapping.get(by, f'resourceId("{value}")')

    def hide_keyboard(self):
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

    def take_screenshot(self, name: str = "screenshot"):
        timestamp = int(time.time())
        path = f"screenshots/{name}_{timestamp}.png"
        self.driver.save_screenshot(path)
        return path
