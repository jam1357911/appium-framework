from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage

# ---------------------------------------------------------------------------
# Locators — replace with real values for your app.
# Keys:   (By strategy, selector string)
# ---------------------------------------------------------------------------
_ANDROID = {
    "username_field":   (AppiumBy.ID, "com.example.fakeapp:id/et_username"),
    "password_field":   (AppiumBy.ID, "com.example.fakeapp:id/et_password"),
    "login_button":     (AppiumBy.ID, "com.example.fakeapp:id/btn_login"),
    "error_message":    (AppiumBy.ID, "com.example.fakeapp:id/tv_error"),
    "forgot_password":  (AppiumBy.ID, "com.example.fakeapp:id/tv_forgot_password"),
}

_IOS = {
    "username_field":   (AppiumBy.ACCESSIBILITY_ID, "usernameTextField"),
    "password_field":   (AppiumBy.ACCESSIBILITY_ID, "passwordTextField"),
    "login_button":     (AppiumBy.ACCESSIBILITY_ID, "loginButton"),
    "error_message":    (AppiumBy.ACCESSIBILITY_ID, "errorLabel"),
    "forgot_password":  (AppiumBy.ACCESSIBILITY_ID, "forgotPasswordButton"),
}


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self._loc = _ANDROID if self._is_android() else _IOS

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def enter_username(self, username: str):
        self.send_keys(self._loc["username_field"], username)

    def enter_password(self, password: str):
        self.send_keys(self._loc["password_field"], password)

    def tap_login(self):
        self.click(self._loc["login_button"])

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.hide_keyboard()
        self.tap_login()

    def tap_forgot_password(self):
        self.click(self._loc["forgot_password"])

    # ------------------------------------------------------------------
    # Assertions / getters
    # ------------------------------------------------------------------

    def is_login_page_displayed(self) -> bool:
        return self.is_element_visible(self._loc["login_button"])

    def get_error_message(self) -> str:
        return self.get_text(self._loc["error_message"])

    def is_error_displayed(self) -> bool:
        return self.is_element_visible(self._loc["error_message"])
