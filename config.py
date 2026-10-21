import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    test_host: str
    api_token: str | None
    cookie: str | None

    @property
    def base_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/x-ndjson, application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "diploma-chat-smoke/1.0",
        }

        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        if self.cookie:
            headers["Cookie"] = self.cookie

        return headers


def get_settings() -> Settings:
    test_host = os.getenv("TEST_HOST", "").strip()
    api_token = os.getenv("API_TOKEN", "").strip() or None
    cookie = os.getenv("COOKIE", "").strip() or None

    if not test_host:
        raise RuntimeError(
            "Environment variable TEST_HOST is required. "
            "Example: http://localhost:8000"
        )

    return Settings(
        test_host=test_host.rstrip("/"),
        api_token=api_token,
        cookie=cookie,
    )
