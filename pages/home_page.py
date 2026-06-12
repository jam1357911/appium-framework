from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage

_ANDROID = {
    "welcome_text":     (AppiumBy.ID, "com.example.fakeapp:id/tv_welcome"),
    "profile_button":   (AppiumBy.ID, "com.example.fakeapp:id/btn_profile"),
    "logout_button":    (AppiumBy.ID, "com.example.fakeapp:id/btn_logout"),
    "item_list":        (AppiumBy.ID, "com.example.fakeapp:id/rv_items"),
    "date_picker":      (AppiumBy.ID, "com.example.fakeapp:id/date_picker"),
    "month_picker":     (AppiumBy.ID, "com.example.fakeapp:id/month_picker"),
    "year_picker":      (AppiumBy.ID, "com.example.fakeapp:id/year_picker"),
}

_IOS = {
    "welcome_text":     (AppiumBy.ACCESSIBILITY_ID, "welcomeLabel"),
    "profile_button":   (AppiumBy.ACCESSIBILITY_ID, "profileButton"),
    "logout_button":    (AppiumBy.ACCESSIBILITY_ID, "logoutButton"),
    "item_list":        (AppiumBy.ACCESSIBILITY_ID, "itemList"),
    "date_picker":      (AppiumBy.ACCESSIBILITY_ID, "datePicker"),
    "month_picker":     (AppiumBy.XPATH, "//XCUIElementTypePickerWheel[1]"),
    "year_picker":      (AppiumBy.XPATH, "//XCUIElementTypePickerWheel[2]"),
}


class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self._loc = _ANDROID if self._is_android() else _IOS

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def tap_profile(self):
        self.click(self._loc["profile_button"])

    def tap_logout(self):
        self.click(self._loc["logout_button"])

    def select_month(self, month: str):
        """Pick a month from the wheel picker on the home screen."""
        self.handle_wheel_picker(self._loc["month_picker"], month)

    def select_year(self, year: str):
        """Pick a year from the wheel picker on the home screen."""
        self.handle_wheel_picker(self._loc["year_picker"], year)

    def scroll_item_list_down(self):
        self.scroll_down_in_element(self._loc["item_list"])

    # ------------------------------------------------------------------
    # Assertions / getters
    # ------------------------------------------------------------------

    def is_home_page_displayed(self) -> bool:
        return self.is_element_visible(self._loc["welcome_text"])

    def get_welcome_text(self) -> str:
        return self.get_text(self._loc["welcome_text"])
