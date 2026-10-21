import allure

from pages.travel_assistant_page import TravelAssistantPage


@allure.epic("Travel Assistant ui")
@allure.feature("Chat opening")
@allure.tag("ui")
@allure.tag("chat")
@allure.tag("opening")
class TestChatOpening:

    @allure.story("Chat title")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke")
    def test_1_chat_title_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_chat_title()

    @allure.story("Greeting")
    @allure.tag("smoke")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_2_greeting_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_greeting()

    @allure.story("Input field visible")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke")
    def test_3_input_field_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_message_input()

    @allure.story("Voice button visible")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke")
    def test_4_voice_button_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_voice_button()

    @allure.story("Close button visible")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke")
    def test_5_close_button_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_close_button()

    @allure.story("Attach file button")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("smoke")
    def test_attach_file_button_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_have_attach_file_button()

    @allure.story("Quick prompts visible")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("smoke")
    def test_6_quick_prompts_visible(self, travel_assistant_widget):
        travel_assistant_widget.should_see_quick_prompt(
            TravelAssistantPage.QUICK_PROMPT_SOCHI,
            "Хочу маршрут в Сочи на 3 дня"
        )
        travel_assistant_widget.should_see_quick_prompt(
            TravelAssistantPage.QUICK_PROMPT_KAZAN,
            "Что делать в Казани на выходных?"
        )
        travel_assistant_widget.should_see_quick_prompt(
            TravelAssistantPage.QUICK_PROMPT_ORDER,
            "Нужна помощь с заказом"
        )
