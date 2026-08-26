"""Size and Duration: immutable value types wrapping parsed sizes and durations.

parse_size and parse_duration hand back a plain int or float, which is
fine for a one-off config read but loses the unit context the moment you
want to compare two values or add them up. These wrappers keep that
context and add the comparisons and arithmetic that come up once you're
working with more than one value at a time -- is this upload under the
limit, what's the total of these poll intervals, and so on.

Both types stay non-negative, matching format_size and format_duration:
negative sizes aren't meaningful, and negative durations need explicit
sign handling that doesn't exist yet.
"""

from __future__ import annotations

from functools import total_ordering

from .durations import format_duration, parse_duration
from .sizes import format_size, parse_size


@total_ordering
class Size:
    """An immutable, non-negative byte count."""

    __slots__ = ("bytes",)

    def __init__(self, n_bytes: int):
        if n_bytes < 0:
            raise ValueError("byte counts cannot be negative")
        self.bytes = int(n_bytes)

    @classmethod
    def parse(cls, text: str, *, source_name: str = "<string>") -> Size:
        return cls(parse_size(text, source_name=source_name))

    def __repr__(self) -> str:
        return f"Size({self.bytes!r})"

    def __str__(self) -> str:
        return format_size(self.bytes)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Size):
            return NotImplemented
        return self.bytes == other.bytes

    def __lt__(self, other: Size) -> bool:
        if not isinstance(other, Size):
            return NotImplemented
        return self.bytes < other.bytes

    def __hash__(self) -> int:
        return hash(self.bytes)

    def __add__(self, other: Size) -> Size:
        if not isinstance(other, Size):
            return NotImplemented
        return Size(self.bytes + other.bytes)

    def __sub__(self, other: Size) -> Size:
        if not isinstance(other, Size):
            return NotImplemented
        return Size(self.bytes - other.bytes)

    def __mul__(self, factor: float) -> Size:
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Size(round(self.bytes * factor))

    __rmul__ = __mul__

    def __truediv__(self, other: Size | float) -> float | Size:
        if isinstance(other, Size):
            return self.bytes / other.bytes
        if isinstance(other, (int, float)):
            return Size(round(self.bytes / other))
        return NotImplemented


@total_ordering
class Duration:
    """An immutable, non-negative duration in seconds."""

    __slots__ = ("seconds",)

    def __init__(self, seconds: float):
        if seconds < 0:
            raise ValueError("durations cannot be negative")
        self.seconds = float(seconds)

    @classmethod
    def parse(cls, text: str, *, source_name: str = "<string>") -> Duration:
        return cls(parse_duration(text, source_name=source_name))

    def __repr__(self) -> str:
        return f"Duration({self.seconds!r})"

    def __str__(self) -> str:
        return format_duration(self.seconds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.seconds == other.seconds

    def __lt__(self, other: Duration) -> bool:
        if not isinstance(other, Duration):
            return NotImplemented
        return self.seconds < other.seconds

    def __hash__(self) -> int:
        return hash(self.seconds)

    def __add__(self, other: Duration) -> Duration:
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(self.seconds + other.seconds)

    def __sub__(self, other: Duration) -> Duration:
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(self.seconds - other.seconds)

    def __mul__(self, factor: float) -> Duration:
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Duration(self.seconds * factor)

    __rmul__ = __mul__

    def __truediv__(self, other: Duration | float) -> float | Duration:
        if isinstance(other, Duration):
            return self.seconds / other.seconds
        if isinstance(other, (int, float)):
            return Duration(self.seconds / other)
        return NotImplemented
