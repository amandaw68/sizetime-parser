"""Parsing for multi-line "key: value" settings files.

This is the glue between the size/duration parsers and an actual config
file: given a schema mapping known keys to a parser (parse_size,
parse_duration, or anything with the same signature), parse_settings reads
a whole file's worth of lines and returns a dict of parsed values, with
errors pointing at the exact line and column in the *file*, not just the
value fragment that failed.
"""

from __future__ import annotations

import re

from .errors import ParseError

_SEPARATOR_RE = re.compile(r"[:=]")


def parse_settings(text: str, schema: dict, *, source_name: str = "<string>") -> dict:
    """Parse a "key: value" (or "key = value") file into a dict.

    schema maps each expected key to a parser callable with the signature
    `(text, *, source_name) -> value`, such as parse_size or parse_duration.

    Blank lines and lines whose first non-space character is "#" are
    ignored. Every key in schema must appear exactly once; unknown keys,
    repeated keys, and missing keys are all errors.

    Example::

        settings = parse_settings(
            "max_upload_size: 50MB\\npoll_interval: 200ms\\n",
            {"max_upload_size": parse_size, "poll_interval": parse_duration},
        )

    Raises ParseError, with a caret pointing at the exact offending
    character in the original file, for a malformed line, an unknown or
    repeated key, a missing key, or a value that fails to parse.
    """
    if not schema:
        raise ValueError("schema must not be empty")

    result: dict = {}
    seen_keys: set = set()
    offset = 0

    for raw_line in text.split("\n"):
        stripped = raw_line.strip()
        if stripped == "" or stripped.startswith("#"):
            offset += len(raw_line) + 1
            continue

        sep_match = _SEPARATOR_RE.search(raw_line)
        if sep_match is None:
            line_start = offset + (len(raw_line) - len(raw_line.lstrip()))
            raise ParseError(
                f"expected 'key: value' or 'key = value', found {stripped!r}",
                text,
                line_start,
                source_name,
            )
        sep_pos = sep_match.start()

        key_text = raw_line[:sep_pos]
        key = key_text.strip()
        key_offset = offset + (len(key_text) - len(key_text.lstrip()))
        if key == "":
            raise ParseError(
                f"expected a key before {raw_line[sep_pos]!r}", text, key_offset, source_name
            )
        if key not in schema:
            expected = ", ".join(sorted(schema))
            raise ParseError(
                f"unknown setting {key!r} (expected one of {expected})",
                text,
                key_offset,
                source_name,
            )
        if key in seen_keys:
            raise ParseError(
                f"setting {key!r} repeated (already set earlier in this file)",
                text,
                key_offset,
                source_name,
            )
        seen_keys.add(key)

        raw_value = raw_line[sep_pos + 1 :]
        lstripped_value = raw_value.lstrip()
        value_offset = offset + sep_pos + 1 + (len(raw_value) - len(lstripped_value))
        value = lstripped_value.rstrip()
        if value == "":
            raise ParseError(f"missing value for {key!r}", text, value_offset, source_name)

        try:
            result[key] = schema[key](value, source_name=source_name)
        except ParseError as err:
            raise ParseError(err.message, text, value_offset + err.offset, source_name) from None

        offset += len(raw_line) + 1

    missing = sorted(set(schema) - seen_keys)
    if missing:
        raise ParseError(
            f"missing required setting(s): {', '.join(missing)}", text, len(text), source_name
        )

    return result
