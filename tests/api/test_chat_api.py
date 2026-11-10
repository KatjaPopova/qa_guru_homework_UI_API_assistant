import httpx
import pytest

from tests.api.helpers.asserts import assert_text_is_russian
from tests.api.helpers.chat import (
    build_answer_text_from_stream,
    send_chat_follow_up_request,
    send_chat_request,
)
from tests.api.helpers.stream import (
    event_types,
    find_suggestions,
    stream_has_status_event,
    stream_has_support_intent,
    stream_has_token,
    validate_event_schema,
)


MIN_ANSWER_LENGTH = 20


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
def test_regular_travel_query_returns_valid_streaming_schema(
    chat_headers: dict[str, str],
    client: httpx.Client,
) -> None:
    query = "Посоветуй идею короткого путешествия по России на выходные"

    stream_events, chat_hash = send_chat_request(client, chat_headers, query)
    answer_text = build_answer_text_from_stream(stream_events)

    assert chat_hash, (
        "В ответе отсутствует x-chat-hash.\n"
        f"Запрос: {query!r}\n"
        f"Полный ответ: {stream_events}"
    )
    assert stream_events, (
        "Streaming-ответ пустой.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}"
    )

    for event in stream_events:
        validate_event_schema(event)

    assert stream_has_status_event(stream_events), (
        "В streaming-ответе отсутствуют status-события.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Типы событий: {event_types(stream_events)}"
    )

    assert answer_text, (
        "Не удалось собрать непустой текст ответа из streaming-событий.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Типы событий: {event_types(stream_events)}"
    )

    assert len(answer_text) > MIN_ANSWER_LENGTH, (
        "Собранный текст ответа слишком короткий.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Текст ответа: {answer_text!r}"
    )

    assert_text_is_russian(
        answer_text,
        context=f"chatHash: {chat_hash}\nЗапрос: {query!r}\n",
    )


@pytest.mark.smoke
def test_ticket_query_without_transport_type_requests_clarification(
    chat_headers: dict[str, str],
    client: httpx.Client,
) -> None:
    query = "Найди билеты из Москвы в Санкт-Петербург на завтра"

    stream_events, chat_hash = send_chat_request(client, chat_headers, query)
    answer_text = build_answer_text_from_stream(stream_events)

    for event in stream_events:
        validate_event_schema(event)

    assert answer_text, (
        "В ответе отсутствует текст уточнения.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Полный ответ: {stream_events}"
    )

    clarification_markers = (
        "уточ",
        "какой транспорт",
        "на чём",
        "на чем",
        "поезд",
        "автобус",
        "самолет",
        "самолёт",
        "вид транспорта",
    )
    normalized_text = answer_text.lower()

    assert any(marker in normalized_text for marker in clarification_markers), (
        "Ожидали вопрос-уточнение по виду транспорта, но не нашли характерных маркеров.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Текст ответа: {answer_text!r}\n"
        f"Типы событий: {event_types(stream_events)}"
    )

    assert not stream_has_token(stream_events, "tickets_card"), (
        "Для неуточнённого ticket-запроса не должны приходить tickets_card.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Полный ответ: {stream_events}"
    )


@pytest.mark.smoke
def test_chat_follow_up_preserves_context(
    chat_headers: dict[str, str],
    client: httpx.Client,
) -> None:
    first_query = "Посоветуй короткую поездку в Казань на выходные"
    follow_up_query = "А что посмотреть там за 1 день?"

    first_stream_events, chat_hash = send_chat_request(client, chat_headers, first_query)
    first_answer_text = build_answer_text_from_stream(first_stream_events)

    assert chat_hash, (
        "После первого сообщения не получили x-chat-hash, continuation невозможен.\n"
        f"Запрос: {first_query!r}\n"
        f"Полный ответ: {first_stream_events}"
    )

    assert first_answer_text, (
        "Первый ответ пустой, невозможно проверить continuation context.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {first_query!r}\n"
        f"Полный ответ: {first_stream_events}"
    )

    follow_up_stream_events = send_chat_follow_up_request(
        client=client,
        chat_headers=chat_headers,
        chat_hash=chat_hash,
        query=follow_up_query,
    )
    follow_up_answer_text = build_answer_text_from_stream(follow_up_stream_events)

    for event in follow_up_stream_events:
        validate_event_schema(event)

    assert follow_up_answer_text, (
        "Follow-up ответ пустой.\n"
        f"chatHash: {chat_hash}\n"
        f"Первый запрос: {first_query!r}\n"
        f"Follow-up запрос: {follow_up_query!r}\n"
        f"Полный ответ: {follow_up_stream_events}"
    )

    kazan_markers = (
        "казан",
        "кремл",
        "бауман",
        "татар",
        "кули",
        "кабан",
        "свиж",
    )
    normalized_follow_up_text = follow_up_answer_text.lower()

    assert any(marker in normalized_follow_up_text for marker in kazan_markers), (
        "Похоже, follow-up не сохранил контекст предыдущего сообщения о Казани.\n"
        f"chatHash: {chat_hash}\n"
        f"Первый запрос: {first_query!r}\n"
        f"Follow-up запрос: {follow_up_query!r}\n"
        f"Текст follow-up ответа: {follow_up_answer_text!r}\n"
        f"Типы событий: {event_types(follow_up_stream_events)}"
    )


@pytest.mark.smoke
def test_regular_travel_query_does_not_trigger_support_or_purchase_tokens(
    chat_headers: dict[str, str],
    client: httpx.Client,
) -> None:
    query = "Посоветуй идею короткого путешествия по России на выходные"

    stream_events, chat_hash = send_chat_request(client, chat_headers, query)
    answer_text = build_answer_text_from_stream(stream_events)

    for event in stream_events:
        validate_event_schema(event)

    assert answer_text, (
        "В обычном travel-запросе ожидаем непустой текстовый ответ.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Полный ответ: {stream_events}"
    )

    assert not stream_has_support_intent(stream_events), (
        "Обычный travel-запрос не должен классифицироваться как Support.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Полный ответ: {stream_events}"
    )

    forbidden_tokens = (
        "purchase_flow_started",
        "avia_card",
        "hotel",
        "room_card",
        "tickets_card",
        "error",
    )
    present_forbidden_tokens = [
        token for token in forbidden_tokens if stream_has_token(stream_events, token)
    ]

    assert not present_forbidden_tokens, (
        "Обычный travel-запрос не должен запускать purchase/support/error flow tokens.\n"
        f"chatHash: {chat_hash}\n"
        f"Запрос: {query!r}\n"
        f"Найдены запрещённые токены: {present_forbidden_tokens}\n"
        f"Типы событий: {event_types(stream_events)}\n"
        f"Полный ответ: {stream_events}"
    )


@pytest.mark.smoke
def test_regular_travel_query_returns_suggestions(
    client: httpx.Client,
    chat_headers: dict[str, str],
) -> None:
    query = "Что посмотреть в Москве?"

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


