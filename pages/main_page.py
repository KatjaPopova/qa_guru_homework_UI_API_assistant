import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MainPage:
    """
    PageObject для главной страницы tutu.ru.
    """

    CAP_CHAT_BUTTON = (
        By.XPATH,
        "//button[.//span[normalize-space()='Кэп']]"
    )

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        with allure.step("Открыть главную страницу tutu.ru"):
            self.driver.get(self.driver.base_url)
        return self

    def open_cap_chat(self):
        with allure.step("Нажать на кнопку открытия чата с Кэпом"):
            button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(self.CAP_CHAT_BUTTON)
            )
            button.click()
        return self
