"""The error type shared by the size and duration parsers.

The goal is that the message alone is enough to fix the input: where the
problem is (line, column), what was found there, and what was expected.
"""

from __future__ import annotations


class ParseError(ValueError):
    """Raised when a size or duration literal cannot be parsed.

    Carries the offset of the offending character in the original source,
    plus the line/column it maps to, so a caller embedding this text in a
    larger document (a config file, a template) can report the mistake at
    the right spot instead of just re-raising a generic ValueError.
    """

    def __init__(self, message: str, source: str, offset: int, source_name: str = "<string>"):
        if not 0 <= offset <= len(source):
            raise ValueError(f"offset {offset} out of range for source of length {len(source)}")
        self.message = message
        self.source = source
        self.offset = offset
        self.source_name = source_name
        self.line, self.column, self._line_text = _locate(source, offset)
        super().__init__(self._render())

    def _render(self) -> str:
        pointer = " " * (self.column - 1) + "^"
        return (
            f"{self.source_name}:{self.line}:{self.column}: {self.message}\n"
            f"    {self._line_text}\n"
            f"    {pointer}"
        )


def _locate(source: str, offset: int) -> tuple[int, int, str]:
    """Turn a flat character offset into a (line, column, line_text) triple.

    Both are 1-indexed to match editor conventions, so they can be pasted
    straight into a "go to line" prompt.
    """
    line_start = source.rfind("\n", 0, offset) + 1
    line_end = source.find("\n", offset)
    if line_end == -1:
        line_end = len(source)
    line_number = source.count("\n", 0, offset) + 1
    column = offset - line_start + 1
    return line_number, column, source[line_start:line_end]
