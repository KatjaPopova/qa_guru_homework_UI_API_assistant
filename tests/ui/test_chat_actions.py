import allure
import pytest

from pages.travel_assistant_page import TravelAssistantPage


@allure.epic("Travel Assistant ui")
@allure.feature("Chat actions")
@allure.tag("ui")
@allure.tag("chat")
class TestChatActions:

    @allure.story("Send text message")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive")
    def test_1_user_can_send_message(self, travel_assistant_widget):
        travel_assistant_widget.send_message("Привет")
        travel_assistant_widget.should_have_sent_message("Привет")
        travel_assistant_widget.should_have_reply_containing_any(
            ["Привет", "Здравствуйте", "чем я могу помочь", "рад помочь"]
        )

    @allure.story("Voice recording")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive")
    def test_2_user_can_start_voice_recording(self, travel_assistant_widget):
        travel_assistant_widget.start_voice_recording()
        travel_assistant_widget.should_have_voice_recording_started()

    @allure.story("Attach file")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive")
    def test_3_user_can_attach_file(self, travel_assistant_widget, tmp_path):
        file_path = tmp_path / "test_file.pdf"
        file_path.write_bytes(b"%PDF-1.4 test pdf file")

        travel_assistant_widget.upload_file_to_chat(str(file_path))
        travel_assistant_widget.should_have_file_upload_response()

    @allure.story("Assistant answers")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive")
    @pytest.mark.parametrize(
        "prompt_locator,prompt_text,expected_reply_part",
        [
            (TravelAssistantPage.QUICK_PROMPT_SOCHI, "Хочу маршрут в Сочи на 3 дня", "Сочи"),
            (TravelAssistantPage.QUICK_PROMPT_KAZAN, "Что делать в Казани на выходных?", "Казань"),
            (TravelAssistantPage.QUICK_PROMPT_ORDER, "Нужна помощь с заказом", "заказ"),
        ]
    )
    def test_quick_prompts_return_answers(
            self,
            travel_assistant_widget,
            prompt_locator,
            prompt_text,
            expected_reply_part
    ):
        travel_assistant_widget.should_see_quick_prompt(prompt_locator, prompt_text)
        travel_assistant_widget.click_quick_prompt(prompt_locator, prompt_text)
        travel_assistant_widget.should_have_sent_message(prompt_text)
        travel_assistant_widget.should_have_reply_containing_any(expected_reply_part)

    @allure.story("Empty message")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative")
    def test_user_cannot_send_empty_message(self, travel_assistant_widget):
        travel_assistant_widget.send_message("")
        travel_assistant_widget.should_not_have_sent_message("")

    @allure.story("Unsupported file format")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative")
    def test_user_cannot_upload_txt_file(self, travel_assistant_widget, tmp_path):
        file_path = tmp_path / "test_file.txt"
        file_path.write_text("Это текстовый файл")

        travel_assistant_widget.upload_file_to_chat(str(file_path))
        travel_assistant_widget.should_have_file_upload_error("test_file.txt")
