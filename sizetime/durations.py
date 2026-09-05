"""Parsing and formatting for human-readable durations.

A duration literal is a number followed by a unit: "500ms", "2.5s", "90m",
"3h", "1d". Unlike sizes, the unit is mandatory here -- a bare "5" is
genuinely ambiguous (seconds? milliseconds?) so it is rejected instead of
guessed at.

Segments can be chained into a compound literal, largest unit first, with
no separator between them: "1h30m20s". Units must strictly decrease and
none may repeat, so "1m1h" and "1h1h" are both rejected -- allowing them
would just invite a value that reads one way and sums another.

A single leading "-" negates the whole literal, e.g. "-1h30m" is thirty
minutes before zero. The sign applies once, up front -- there is no such
thing as "-1h-30m", since a sign on every segment would just raise the
question of what a mixed-sign literal like "-1h30m" is supposed to mean.
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
    """Parse a duration literal such as "250ms", "1.5h", or "1h30m20s" into seconds.

    A compound literal is a sequence of number+unit segments glued together
    with no space between them, written largest unit first ("1h30m", not
    "30m1h" or "1h 30m"). A single leading "-" negates the whole literal
    ("-1h30m").

    Raises ParseError, with a caret pointing at the exact offending
    character, for empty input, a malformed number, a missing or unknown
    unit, a unit repeated or out of order, or trailing garbage after a
    valid literal.
    """
    if text.strip() == "":
        raise ParseError("expected a duration, found an empty string", text, 0, source_name)

    expected = ", ".join(sorted(_UNITS_TO_SECONDS))

    pos = _skip_spaces(text, 0)
    negative = False
    if pos < len(text) and text[pos] == "-":
        negative = True
        pos += 1

    total = 0.0
    seen_units: list[str] = []

    while True:
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
        if unit_key in seen_units:
            raise ParseError(
                f"time unit {unit_text!r} repeated (already used earlier in this duration)",
                text,
                unit_start,
                source_name,
            )
        if seen_units and _UNITS_TO_SECONDS[unit_key] >= _UNITS_TO_SECONDS[seen_units[-1]]:
            raise ParseError(
                f"time unit {unit_text!r} is out of order "
                "(compound durations go from largest to smallest unit, e.g. '1h30m')",
                text,
                unit_start,
                source_name,
            )
        seen_units.append(unit_key)
        total += number * _UNITS_TO_SECONDS[unit_key]

        if pos < len(text) and (text[pos].isdigit() or text[pos] == "."):
            continue

        pos = _skip_spaces(text, pos)
        if pos != len(text):
            raise ParseError(
                f"unexpected text {text[pos:]!r} after {text[:pos].strip()!r}",
                text,
                pos,
                source_name,
            )
        return -total if negative else total


def format_duration(seconds: float) -> str:
    """Format a number of seconds as a human-readable duration string.

    Picks the largest unit that keeps the displayed number at least 1, so
    results read naturally ("1.50h" rather than "5400.00s"). Negative
    values get a leading "-" ("-1.50h"); the magnitude is formatted the
    same way as a positive one.
    """
    if seconds == 0:
        return "0s"

    sign = "-" if seconds < 0 else ""
    magnitude = abs(seconds)

    for unit, unit_seconds in _FORMAT_UNITS:
        if magnitude >= unit_seconds:
            return f"{sign}{magnitude / unit_seconds:.2f}{unit}"

    return f"{sign}{magnitude / 1e-9:.2f}ns"


def _skip_spaces(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] in " \t":
        pos += 1
    return pos
