import os
from urllib.parse import quote
import httpx

from config import Settings, get_settings

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from pages.main_page import MainPage
from pages.travel_assistant_page import TravelAssistantPage
from utils import attach

load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="https://www.tutu.ru",
        help="Base URL of the application"
    )

    parser.addoption(
        "--remote-url",
        action="store",
        default="https://selenoid.qa.guru/wd/hub",
        help="Адрес Selenoid",
    )

    parser.addoption(
        "--remote",
        action="store",
        choices=["true", "false"],
        default="false",
        help="Запускать тесты удаленно через Selenoid",
    )

    parser.addoption(
        "--browser",
        action="store",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Браузер: chrome или firefox",
    )

    parser.addoption(
        "--browser-version",
        action="store",
        default="latest",
        help="Версия браузера",
    )

    parser.addoption(
        "--headless",
        action="store",
        choices=["true", "false"],
        default="false",
        help="Headless-режим: true или false",
    )

    parser.addoption(
        "--window-size",
        action="store",
        default="1920x1080",
        help="Разрешение экрана, например 1920x1080",
    )


def get_window_size(value):
    try:
        width, height = value.lower().split("x")
        return int(width), int(height)
    except ValueError:
        raise pytest.UsageError(
            "--window-size нужно указать в формате 1920x1080"
        )


@pytest.fixture(scope="function")
def driver(request):
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")

    if not login:
        pytest.fail("В файле .env не указана переменная LOGIN")

    if not password:
        pytest.fail("В файле .env не указана переменная PASSWORD")

    base_url = request.config.getoption("--base-url")
    remote_mode = request.config.getoption("--remote")
    browser_name = request.config.getoption("--browser")
    browser_version = request.config.getoption("--browser-version")
    headless = request.config.getoption("--headless")
    window_size = request.config.getoption("--window-size")

    width, height = get_window_size(window_size)

    options = ChromeOptions()
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")

    if headless == "true":
        options.add_argument("--headless=new")

    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    if remote_mode == "true":
        remote_url = request.config.getoption("--remote-url")

        options.set_capability("browserName", browser_name)
        options.set_capability("browserVersion", browser_version)
        options.set_capability(
            "selenoid:options",
            {
                "enableVNC": True,
                "enableVideo": True,
                "screenResolution": f"{width}x{height}x24",
            },
        )

        encoded_login = quote(login, safe="")
        encoded_password = quote(password, safe="")

        command_executor = remote_url.replace(
            "://",
            f"://{encoded_login}:{encoded_password}@",
            1,
        )

        driver = webdriver.Remote(
            command_executor=command_executor,
            options=options,
        )
    else:
        driver = webdriver.Chrome(options=options)

    driver.base_url = base_url

    yield driver

    try:
        attach.add_screenshot(driver)
        attach.add_html(driver)
        attach.add_logs(driver)
        if remote_mode == "true":
            attach.add_video(driver)
    finally:
        driver.quit()


@pytest.fixture
def main_page(driver, request):
    base_url = request.config.getoption("--base-url")
    page = MainPage(driver)
    page.open(base_url)
    return page


@pytest.fixture
def travel_assistant_widget(main_page):
    main_page.open_cap_chat()
    return TravelAssistantPage(main_page.driver)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def client(settings: Settings) -> httpx.Client:
    with httpx.Client(
        base_url=settings.test_host,
        timeout=httpx.Timeout(60.0, connect=20.0),
        follow_redirects=True,
    ) as http_client:
        yield http_client


@pytest.fixture(scope="session")
def chat_headers(settings: Settings) -> dict[str, str]:
    return settings.base_headers.copy()