import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver_helper import DriverHelper


class TravelAssistantPage:
    CHAT_TITLE = (By.CSS_SELECTOR, "h2[data-ti='heading-2']")
    GREETING = (
        By.XPATH,
        "//h2[normalize-space()='Привет, я Кэп!']"
    )

    MESSAGE_INPUT = (By.CSS_SELECTOR, "textarea[placeholder='Напишите запрос']")
    MESSAGE_TEXTS = (By.CSS_SELECTOR, "p[data-ti='p']")

    VOICE_BUTTON = (By.CSS_SELECTOR, "button[aria-label='Начать запись']")
    STOP_VOICE_BUTTON = (By.CSS_SELECTOR, "button[aria-label='Остановить запись']")

    ATTACH_FILE_BUTTON = (
        By.XPATH,
        "//button[.//i[contains(@class, 'oim-paper-clip_outline')]]"
    )
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")

    CLOSE_BUTTON = (
        By.CSS_SELECTOR,
        "button[data-ti='close-button']"
    )

    FILE_UPLOAD_ERROR = (
        By.XPATH,
        "//*[contains(text(), 'Приемлемые типы файлов')]"
    )

    IFRAME = (By.CSS_SELECTOR, "iframe.tutu-chat-widget-iframe")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        self.helper = DriverHelper(driver, timeout=20)

    def open(self, url):
        with allure.step(f"Открыть страницу: {url}"):
            self.helper.open(url)
        return self

    def _switch_to_iframe(self):
        self.helper.switch_to_frame(self.IFRAME)

    def _switch_to_default_content(self):
        self.helper.switch_to_default_content()

    def _wait_visible(self, locator):
        return self.helper.wait_visible(locator)

    def _wait_clickable(self, locator):
        return self.helper.wait_clickable(locator)

    def _wait_presence(self, locator):
        return self.helper.wait_presence(locator)

    def _wait_message_contains(self, text: str):
        return self.helper.wait_message_contains(self.MESSAGE_TEXTS, text)

    def _wait_message_equals(self, text: str):
        return self.helper.wait_message_equals(self.MESSAGE_TEXTS, text)

    @staticmethod
    def _quick_prompt_locator(prompt_text: str):
        normalized_prompt = " ".join(prompt_text.split())
        significant_part = normalized_prompt.rstrip("?").split(",")[0]
        return By.XPATH, f'//button[contains(normalize-space(.), "{significant_part}")]'

    # -------------------------
    # CHECKS
    # -------------------------

    def should_have_chat_title(self):
        with allure.step("Проверить заголовок чата"):
            self._wait_visible(self.CHAT_TITLE)
        return self

    def should_have_greeting(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить приветствие"):
                self._wait_visible(self.GREETING)
        finally:
            self._switch_to_default_content()
        return self

    def should_see_quick_prompt(self, prompt_text: str):
        self._switch_to_iframe()
        try:
            with allure.step(f"Проверить подсказку: {prompt_text}"):
                self._wait_visible(self._quick_prompt_locator(prompt_text))
        finally:
            self._switch_to_default_content()
        return self

    def should_have_voice_button(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить кнопку голосового ввода"):
                self._wait_visible(self.VOICE_BUTTON)
        finally:
            self._switch_to_default_content()
        return self

    def should_have_message_input(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить поле ввода сообщения"):
                self._wait_visible(self.MESSAGE_INPUT)
        finally:
            self._switch_to_default_content()
        return self

    def should_have_close_button(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить кнопку закрытия чата"):
                self._wait_presence(self.CLOSE_BUTTON)
        finally:
            self._switch_to_default_content()
        return self

    def should_have_attach_file_button(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить кнопку прикрепления файла"):
                self._wait_clickable(self.ATTACH_FILE_BUTTON)
        finally:
            self._switch_to_default_content()
        return self

    def should_not_have_sent_message(self, text: str):
        self._switch_to_iframe()
        try:
            with allure.step(f'Проверить, что сообщение "{text}" не появилось в чате'):
                elements = self.driver.find_elements(*self.MESSAGE_TEXTS)
                assert not any(el.text.strip() == text for el in elements), (
                    f'Сообщение "{text}" не должно было появиться в чате'
                )
        finally:
            self._switch_to_default_content()
        return self

    def should_have_file_upload_error(self, file_name: str):
        self._switch_to_iframe()
        try:
            wait = WebDriverWait(self.driver, 20)

            with allure.step(f"Проверить, что файл {file_name} отклонён"):
                def _predicate(driver):
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    return "Файлы с ошибкой" in body_text and file_name in body_text

                assert wait.until(_predicate), (
                    f'Ожидалось сообщение об ошибке для файла {file_name}'
                )
        finally:
            self._switch_to_default_content()
        return self

    # -------------------------
    # ACTIONS
    # -------------------------

    def send_message(self, text: str):
        self._switch_to_iframe()
        try:
            with allure.step(f'Отправить сообщение: "{text}"'):
                input_field = self._wait_visible(self.MESSAGE_INPUT)
                input_field.clear()
                input_field.send_keys(text)
                input_field.send_keys(Keys.ENTER)
        finally:
            self._switch_to_default_content()
        return self

    def start_voice_recording(self):
        self._switch_to_iframe()
        try:
            with allure.step("Нажать кнопку голосового ввода"):
                button = self._wait_clickable(self.VOICE_BUTTON)
                button.click()
        finally:
            self._switch_to_default_content()
        return self

    def upload_file_to_chat(self, file_path: str):
        self._switch_to_iframe()
        try:
            with allure.step(f"Загрузить файл: {file_path}"):
                file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
                file_input.send_keys(file_path)
        finally:
            self._switch_to_default_content()
        return self

    # -------------------------
    # ASSERTIONS AFTER ACTIONS
    # -------------------------

    def should_have_sent_message(self, text: str):
        self._switch_to_iframe()
        try:
            with allure.step(f'Проверить, что сообщение "{text}" появилось в чате'):
                assert self._wait_message_equals(text), f'Сообщение "{text}" не найдено в чате'
        finally:
            self._switch_to_default_content()
        return self

    def should_have_reply_containing_any(self, expected_texts, timeout=60):
        self._switch_to_iframe()
        try:
            wait = WebDriverWait(self.driver, timeout)

            with allure.step(f"Проверить, что ответ ассистента содержит один из вариантов: {expected_texts}"):
                def _predicate(driver):
                    elements = driver.find_elements(*self.MESSAGE_TEXTS)
                    return any(
                        any(expected_text in el.text for expected_text in expected_texts)
                        for el in elements
                    )

                assert wait.until(_predicate), (
                    f'Ответ ассистента не содержит ни одного из ожидаемых вариантов: {expected_texts}'
                )
        finally:
            self._switch_to_default_content()
        return self

    def should_have_voice_recording_started(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить, что запись голоса началась"):
                self._wait_visible(self.STOP_VOICE_BUTTON)
        finally:
            self._switch_to_default_content()
        return self

    def should_have_file_upload_response(self):
        self._switch_to_iframe()
        try:
            with allure.step("Проверить реакцию чата после загрузки файла"):
                wait = WebDriverWait(self.driver, 20)

                try:
                    error_text = wait.until(lambda driver: driver.find_element(*self.FILE_UPLOAD_ERROR).text.strip())
                    raise AssertionError(
                        f'После загрузки файла появилось сообщение об ошибке: "{error_text}"'
                    )
                except TimeoutException:
                    pass

                self._wait_visible(self.MESSAGE_INPUT)
        finally:
            self._switch_to_default_content()
        return self

    def click_quick_prompt(self, prompt_text: str):
        self._switch_to_iframe()
        try:
            with allure.step(f"Нажать подсказку: {prompt_text}"):
                button = self._wait_visible(self._quick_prompt_locator(prompt_text))
                button.click()
        finally:
            self._switch_to_default_content()
        return self
