"""Parsing and formatting for human-readable byte sizes.

Two unit families are recognised:
  decimal: B, KB, MB, GB, TB, PB      (powers of 1000)
  binary:  KiB, MiB, GiB, TiB, PiB    (powers of 1024)

"10MB", "10 MB", "10mb" and "10.5GiB" are all accepted; a bare number is
treated as a byte count, since that is how sizes usually show up in the
wild (Content-Length headers, stat() results, and so on).
"""

from __future__ import annotations

import re

from .errors import ParseError

_DECIMAL_UNITS = {
    "b": 1,
    "kb": 1000,
    "mb": 1000**2,
    "gb": 1000**3,
    "tb": 1000**4,
    "pb": 1000**5,
}

_BINARY_UNITS = {
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
}

_UNITS = {**_DECIMAL_UNITS, **_BINARY_UNITS}

_NUMBER_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_UNIT_RE = re.compile(r"[A-Za-z]*")


def parse_size(text: str, *, source_name: str = "<string>") -> int:
    """Parse a byte size literal such as "512KB" or "2 GiB" into a byte count.

    Raises ParseError, with a caret pointing at the exact offending
    character, for empty input, a malformed number, an unknown unit, or
    trailing garbage after a valid literal.
    """
    if text.strip() == "":
        raise ParseError("expected a byte size, found an empty string", text, 0, source_name)

    pos = _skip_spaces(text, 0)

    number_match = _NUMBER_RE.match(text, pos)
    if number_match is None:
        found = repr(text[pos]) if pos < len(text) else "end of input"
        raise ParseError(f"expected a number, found {found}", text, pos, source_name)
    pos = number_match.end()
    number = float(number_match.group())

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

    if unit_text == "":
        return round(number)

    unit_key = unit_text.lower()
    if unit_key not in _UNITS:
        expected = ", ".join(sorted(u.upper() for u in _UNITS))
        raise ParseError(
            f"unknown size unit {unit_text!r} (expected one of {expected})",
            text,
            unit_start,
            source_name,
        )

    return round(number * _UNITS[unit_key])


def format_size(n_bytes: int, *, binary: bool = False) -> str:
    """Format a byte count as a human-readable string.

    binary=False uses decimal units (1000-based, the SI convention);
    binary=True uses binary units (1024-based, what most file browsers
    actually display).
    """
    if n_bytes < 0:
        raise ValueError("byte counts cannot be negative")

    base = 1024 if binary else 1000
    suffixes = ["", "Ki", "Mi", "Gi", "Ti", "Pi"] if binary else ["", "K", "M", "G", "T", "P"]

    value = float(n_bytes)
    for suffix in suffixes[:-1]:
        if value < base:
            return f"{int(value)}B" if suffix == "" else f"{value:.1f}{suffix}B"
        value /= base
    return f"{value:.1f}{suffixes[-1]}B"


def _skip_spaces(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] in " \t":
        pos += 1
    return pos
