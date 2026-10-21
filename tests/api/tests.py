import httpx
import pytest

from tests.api.helpers.chat import build_answer_text_from_stream, send_chat_request
from tests.api.helpers.stream import (
    event_types,
    find_suggestions,
    stream_has_support_intent,
    validate_event_schema,
)
from tests.api.testdata.cases import SAFETY_QUERIES, SECURITY_QUERIES
from tests.api.testdata.expected_texts import COMMON_REFUSAL_TEXT


def assert_non_empty_answer(answer_text: str) -> None:
    assert answer_text.strip(), "Assistant answer is empty"


def assert_contains_any(text: str, keywords: list[str], message: str) -> None:
    normalized_text = text.lower()
    assert any(keyword.lower() in normalized_text for keyword in keywords), (
        f"{message}\n"
        f"Expected one of keywords: {keywords}\n"
        f"Actual text: {text}"
    )


@pytest.mark.smoke
def test_regular_travel_query_returns_meaningful_answer(
    client: httpx.Client,
    chat_headers: dict[str, str],
) -> None:
    query = "Куда поехать на выходные из Москвы?"

    stream_events, chat_hash = send_chat_request(client, chat_headers, query)

    assert chat_hash is None or isinstance(chat_hash, str)

    for event in stream_events:
        validate_event_schema(event)

    types = event_types(stream_events)
    assert "t" in types, f"No text events found in stream. Event types: {types}"

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    assert_contains_any(
        answer_text,
        ["поехать", "выходные", "москв", "поездк", "вариант", "маршрут", "направление"],
        "Travel answer does not look meaningful",
    )

    assert not stream_has_support_intent(stream_events), (
        "Support intent must not appear in a normal travel scenario"
    )

    assert answer_text.strip() != COMMON_REFUSAL_TEXT.strip(), (
        "Regular travel query unexpectedly returned refusal text"
    )


@pytest.mark.smoke
def test_regular_travel_query_returns_suggestions(
    client: httpx.Client,
    chat_headers: dict[str, str],
) -> None:
    query = "Куда поехать на выходные из Москвы?"

    stream_events, _ = send_chat_request(client, chat_headers, query)

    for event in stream_events:
        validate_event_schema(event)

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    suggestions = find_suggestions(stream_events)
    assert suggestions is not None, "Expected suggestions in stream, but none were found"
    assert len(suggestions) > 0, "Suggestions list is empty"
    assert any(isinstance(item, str) and item.strip() for item in suggestions), (
        f"Suggestions must contain non-empty texts. Actual suggestions: {suggestions}"
    )


@pytest.mark.smoke
def test_hotel_query_without_dates_requests_clarification(
    client: httpx.Client,
    chat_headers: dict[str, str],
) -> None:
    query = "Найди отель в Казани на двоих"

    stream_events, _ = send_chat_request(client, chat_headers, query)

    for event in stream_events:
        validate_event_schema(event)

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    assert_contains_any(
        answer_text,
        ["дата", "даты", "когда", "заезд", "выезд"],
        "Hotel query without dates did not trigger date clarification",
    )


@pytest.mark.smoke
def test_flight_query_without_origin_requests_clarification(
    client: httpx.Client,
    chat_headers: dict[str, str],
) -> None:
    query = "Найди авиабилеты в Сочи на 10 июня для одного пассажира"

    stream_events, _ = send_chat_request(client, chat_headers, query)

    for event in stream_events:
        validate_event_schema(event)

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    assert_contains_any(
        answer_text,
        ["откуда", "город вылета", "город отправления", "из какого города", "вылет"],
        "Flight query without origin did not trigger origin clarification",
    )


@pytest.mark.smoke
@pytest.mark.parametrize("query", SECURITY_QUERIES)
def test_security_query_returns_refusal(
    client: httpx.Client,
    chat_headers: dict[str, str],
    query: str,
) -> None:
    stream_events, _ = send_chat_request(client, chat_headers, query)

    for event in stream_events:
        validate_event_schema(event)

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    assert answer_text.strip() == COMMON_REFUSAL_TEXT.strip(), (
        "Security query did not return expected refusal text.\n"
        f"Expected: {COMMON_REFUSAL_TEXT}\n"
        f"Actual: {answer_text}"
    )


@pytest.mark.smoke
@pytest.mark.parametrize("query", SAFETY_QUERIES)
def test_safety_sensitive_topic_returns_refusal(
    client: httpx.Client,
    chat_headers: dict[str, str],
    query: str,
) -> None:
    stream_events, _ = send_chat_request(client, chat_headers, query)

    for event in stream_events:
        validate_event_schema(event)

    answer_text = build_answer_text_from_stream(stream_events)
    assert_non_empty_answer(answer_text)

    assert answer_text.strip() == COMMON_REFUSAL_TEXT.strip(), (
        "Safety-sensitive query did not return expected refusal text.\n"
        f"Expected: {COMMON_REFUSAL_TEXT}\n"
        f"Actual: {answer_text}"
    )