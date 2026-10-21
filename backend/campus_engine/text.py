"""Small formatting helpers shared by the engine's plain-language explanations."""
from __future__ import annotations

from datetime import date

_PLURALS = {"quiz": "quizzes"}


def rand(cents: int) -> str:
    """Format cents as rand, South African style: R1 240 or R1 240.50."""
    sign = "-" if cents < 0 else ""
    whole, part = divmod(abs(int(cents)), 100)
    text = f"{whole:,}".replace(",", " ")
    return f"{sign}R{text}" + (f".{part:02d}" if part else "")


def day(d: date) -> str:
    """Format a date as 'Mon 19 Oct'."""
    return f"{d:%a} {d.day} {d:%b}"


def long_day(d: date) -> str:
    """Format a date as 'Mon 19 Oct 2026', for dates that may fall in another year."""
    return f"{day(d)} {d.year}"


def in_days(n: int) -> str:
    """'today', 'tomorrow' or 'in 12 days'."""
    if n == 0:
        return "today"
    if n == 1:
        return "tomorrow"
    return f"in {plural(n, 'day')}"


def plural(n: int, word: str) -> str:
    return f"{n} {word if n == 1 else _PLURALS.get(word, word + 's')}"


def join(parts: list[str]) -> str:
    """Join with commas and a final 'and'."""
    parts = [p for p in parts if p]
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def num(x: float) -> str:
    """Print a number without a pointless '.0'."""
    return f"{x:g}"
