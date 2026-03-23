from __future__ import annotations

import math
import re


MULTIPLIERS = {
    "K": 1_000,
    "M": 1_000_000,
    "B": 1_000_000_000,
    "T": 1_000_000_000_000,
}

SIGN_TRANSLATION = str.maketrans(
    {
        "\u2212": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\uFF0B": "+",
    }
)


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.replace("\xa0", " ").replace("\u202f", " ").split())


def parse_compact_number(value: str | None) -> float | None:
    text = normalize_text(value)
    if not text:
        return None

    text = text.translate(SIGN_TRANSLATION).replace("%", "").replace(",", "")
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*([KMBT])?", text)
    if not match:
        return None

    number = float(match.group(1))
    suffix = match.group(2)
    if suffix:
        number *= MULTIPLIERS[suffix]
    return number


def parse_currency(value: str | None) -> float | None:
    return parse_compact_number(value)


def parse_percent(value: str | None) -> float | None:
    return parse_compact_number(value)


def safe_float(value: float | None, default: float = math.nan) -> float:
    if value is None:
        return default
    return value
