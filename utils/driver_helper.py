from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class DriverHelper:
    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        self.driver.get(url)

    def switch_to_frame(self, locator):
        iframe = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.switch_to.frame(iframe)

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_presence(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_message_contains(self, locator, text: str):
        def _predicate(driver):
            try:
                elements = driver.find_elements(*locator)
                texts = [element.text.strip() for element in elements]
                return any(text in message for message in texts)
            except StaleElementReferenceException:
                return False

        return self.wait.until(_predicate)

    def wait_message_equals(self, locator, text: str):
        def _predicate(driver):
            try:
                elements = driver.find_elements(*locator)
                texts = [element.text.strip() for element in elements]
                return any(message == text for message in texts)
            except StaleElementReferenceException:
                return False

        return self.wait.until(_predicate)