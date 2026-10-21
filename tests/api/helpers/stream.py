from typing import Any


def validate_event_schema(event: dict[str, Any]) -> None:
    assert "t" in event, f"Event does not contain 't': {event}"
    assert "c" in event, f"Event does not contain 'c': {event}"
    assert isinstance(event["t"], str), f"Event field 't' must be a string: {event}"


def event_types(stream_events: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []

    for event in stream_events:
        event_type = event.get("t")
        if isinstance(event_type, str):
            result.append(event_type)

    return sorted(result)


def _normalize_suggestion_item(item: Any) -> str | None:
    if isinstance(item, str):
        text = item.strip()
        return text or None

    if isinstance(item, dict):
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()

    return None


def find_suggestions(stream_events: list[dict[str, Any]]) -> list[str] | None:
    """
    Ищет suggestions в serviceData и нормализует их в list[str].

    Поддерживает форматы:
    - {"suggestions": {"a": "text1", "b": "text2"}}
    - {"suggestions": ["text1", "text2"]}
    - {"suggestions": [{"text": "text1"}, {"text": "text2"}]}
    """
    for event in stream_events:
        if event.get("t") != "serviceData":
            continue

        content = event.get("c")
        if not isinstance(content, dict):
            continue

        suggestions = content.get("suggestions")

        if isinstance(suggestions, dict) and suggestions:
            normalized = [_normalize_suggestion_item(item) for item in suggestions.values()]
        elif isinstance(suggestions, list) and suggestions:
            normalized = [_normalize_suggestion_item(item) for item in suggestions]
        else:
            continue

        result = [item for item in normalized if item]
        if result:
            return result

    return None


def stream_has_support_intent(stream_events: list[dict[str, Any]]) -> bool:
    """
    Проверяет наличие support intent в стриме:
    {"t": "i", "c": "Support"}
    """
    return any(
        event.get("t") == "i" and event.get("c") == "Support"
        for event in stream_events
    )