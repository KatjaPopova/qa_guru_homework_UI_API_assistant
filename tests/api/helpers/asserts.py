CYRILLIC_RANGES = (
    (0x0400, 0x04FF),
    (0x0500, 0x052F),
)


def _is_cyrillic_letter(char: str) -> bool:
    code_point = ord(char)
    return any(start <= code_point <= end for start, end in CYRILLIC_RANGES)


def russian_letters_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0

    cyrillic_letters_count = sum(1 for char in letters if _is_cyrillic_letter(char))
    return cyrillic_letters_count / len(letters)


def assert_text_is_russian(text: str, *, min_ratio: float = 0.8, context: str = "") -> None:
    ratio = russian_letters_ratio(text)
    assert ratio >= min_ratio, (
        "Текст ответа не похож на русский язык.\n"
        f"Ожидали долю кириллицы >= {min_ratio}, фактически: {ratio:.2f}\n"
        f"{context}"
        f"Текст ответа: {text!r}"
    )