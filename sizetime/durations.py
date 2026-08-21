"""Parsing and formatting for human-readable durations.

A duration literal is a number followed by a unit: "500ms", "2.5s", "90m",
"3h", "1d". Unlike sizes, the unit is mandatory here -- a bare "5" is
genuinely ambiguous (seconds? milliseconds?) so it is rejected instead of
guessed at.

Compound literals like "1h30m" are not supported yet; write "90m" or
"5400s" instead.
"""

from __future__ import annotations

import re

from .errors import ParseError

_UNITS_TO_SECONDS = {
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "m": 60.0,
    "h": 3600.0,
    "d": 86400.0,
}

_FORMAT_UNITS = (
    ("d", 86400.0),
    ("h", 3600.0),
    ("m", 60.0),
    ("s", 1.0),
    ("ms", 1e-3),
    ("us", 1e-6),
)

_NUMBER_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_UNIT_RE = re.compile(r"[A-Za-z]*")


def parse_duration(text: str, *, source_name: str = "<string>") -> float:
    """Parse a duration literal such as "250ms" or "1.5h" into seconds.

    Raises ParseError, with a caret pointing at the exact offending
    character, for empty input, a malformed number, a missing or unknown
    unit, or trailing garbage after a valid literal.
    """
    if text.strip() == "":
        raise ParseError("expected a duration, found an empty string", text, 0, source_name)

    pos = _skip_spaces(text, 0)

    number_match = _NUMBER_RE.match(text, pos)
    if number_match is None:
        found = repr(text[pos]) if pos < len(text) else "end of input"
        raise ParseError(f"expected a number, found {found}", text, pos, source_name)
    pos = number_match.end()
    number_text = number_match.group()
    number = float(number_text)

    pos = _skip_spaces(text, pos)
    unit_start = pos
    unit_match = _UNIT_RE.match(text, pos)
    pos = unit_match.end()
    unit_text = unit_match.group()

    pos = _skip_spaces(text, pos)
    if pos != len(text):
        raise ParseError(
            f"unexpected text {text[pos:]!r} after {text[:pos].strip()!r}",
            text,
            pos,
            source_name,
        )

    expected = ", ".join(sorted(_UNITS_TO_SECONDS))

    if unit_text == "":
        raise ParseError(
            f"missing time unit after {number_text!r} (expected one of {expected})",
            text,
            unit_start,
            source_name,
        )

    unit_key = unit_text.lower()
    if unit_key not in _UNITS_TO_SECONDS:
        raise ParseError(
            f"unknown time unit {unit_text!r} (expected one of {expected})",
            text,
            unit_start,
            source_name,
        )

    return number * _UNITS_TO_SECONDS[unit_key]


def format_duration(seconds: float) -> str:
    """Format a number of seconds as a human-readable duration string.

    Picks the largest unit that keeps the displayed number at least 1, so
    results read naturally ("1.50h" rather than "5400.00s").
    """
    if seconds < 0:
        raise ValueError("durations cannot be negative")
    if seconds == 0:
        return "0s"

    for unit, unit_seconds in _FORMAT_UNITS:
        if seconds >= unit_seconds:
            return f"{seconds / unit_seconds:.2f}{unit}"

    return f"{seconds / 1e-9:.2f}ns"


def _skip_spaces(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] in " \t":
        pos += 1
    return pos
