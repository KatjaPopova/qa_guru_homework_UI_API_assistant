import datetime as dt
import json
from typing import Any

import httpx


CHAT_ENDPOINT = "/api/v2/chats/"


def parse_jsonl_response(response: httpx.Response, expected_status: int = 200) -> list[dict[str, Any]]:
    assert response.status_code == expected_status, (
        f"Unexpected status code: {response.status_code}\n"
        f"Response headers: {dict(response.headers)}\n"
        f"Response text: {response.text[:3000]}"
    )

    raw_text = response.text.strip()
    assert raw_text, "Response body is empty"

    events: list[dict[str, Any]] = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Invalid JSONL line: {line}") from exc

        assert isinstance(item, dict), f"Each JSONL item must be an object, got: {type(item)}"
        events.append(item)

    assert events, "No JSONL events found in response"
    return events


def build_answer_text_from_stream(stream_events: list[dict[str, Any]]) -> str:
    """
    Собирает ответ ассистента из текстовых стрим-событий.
    Базовый ожидаемый формат:
    {"t": "t", "c": "..."}
    """
    chunks: list[str] = []

    for event in stream_events:
        if event.get("t") == "t" and isinstance(event.get("c"), str):
            chunks.append(event["c"])

    return "".join(chunks).strip()


def send_chat_request(
    client: httpx.Client,
    chat_headers: dict[str, str],
    query: str,
) -> tuple[list[dict[str, Any]], str | None]:
    payload = [
        {
            "role": "user",
            "content": query,
            "dateCreated": dt.datetime.utcnow().isoformat(),
        }
    ]

    response = client.post(
        CHAT_ENDPOINT,
        headers=chat_headers,
        json=payload,
    )

    stream_events = parse_jsonl_response(response, expected_status=200)
    chat_hash = response.headers.get("x-chat-hash")
    return stream_events, chat_hash