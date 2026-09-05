# sizetime

Parse and format byte sizes ("10MB", "2.5GiB") and durations ("500ms",
"1.5h") from plain strings. Standard library only, no dependencies.

## Why

Config files, CLI flags, and API responses are full of values like
`max_upload_size: 50MB` or `poll_interval: 200ms`. Writing that parsing
by hand is easy to get almost right, and then annoying to debug when a
user writes `50 Mb` or `50MG` and gets a bare `ValueError` with no
indication of what was wrong or where.

sizetime parses these values and, when it can't, says exactly what it
expected and exactly which character it choked on:

```
>>> from sizetime import parse_size
>>> parse_size("50 MG")
Traceback (most recent call last):
  ...
sizetime.errors.ParseError: <string>:1:4: unknown size unit 'MG' (expected one of B, GB, GIB, KB, KIB, MB, MIB, PB, PIB, TB, TIB)
    50 MG
       ^
```

## Usage

```python
from sizetime import parse_size, parse_duration, format_size, format_duration

parse_size("512KB")        # -> 512000
parse_size("1GiB")         # -> 1073741824
parse_size("100")          # -> 100 (a bare number is a byte count)

parse_duration("250ms")    # -> 0.25
parse_duration("1.5h")     # -> 5400.0
parse_duration("1h30m20s") # -> 5420.0

format_size(1_500_000)                # -> "1.5MB"
format_size(1_500_000, binary=True)   # -> "1.4MiB"
format_duration(90)                   # -> "1.50m"
```

`Size` and `Duration` wrap the parsed number so it keeps its unit context
past the point where you'd otherwise be looking at a bare int or float.
They're immutable, comparable, hashable, and support the arithmetic you'd
expect -- add two, scale one by a factor, or divide one by another to get
a ratio:

```python
from sizetime import Duration, Size

upload_limit = Size.parse("50MB")
if Size(len(payload)) > upload_limit:
    raise ValueError(f"payload too large: {Size(len(payload))} > {upload_limit}")

total = Duration.parse("1h30m") + Duration.parse("15m")  # -> Duration(6300.0)
```

Both types stay non-negative: constructing one below zero, or subtracting
a larger value from a smaller one, raises `ValueError`, the same as
`format_size` and `format_duration` do today.

For a whole config file at once, `parse_settings` takes a schema mapping
each expected key to a parser (`parse_size`, `parse_duration`, or your
own) and returns a dict, with errors pointing at the exact line in the
file rather than just the value that failed:

```python
from sizetime import parse_settings, parse_size, parse_duration

config = parse_settings(
    open("app.conf").read(),
    {"max_upload_size": parse_size, "poll_interval": parse_duration},
)
# -> {"max_upload_size": 50000000, "poll_interval": 0.2}
```

Lines are `key: value` or `key = value`; blank lines and lines starting
with `#` are ignored. Unknown keys, repeated keys, and missing keys are
all reported as `ParseError`s.

Every parse error is a `sizetime.ParseError` (a `ValueError` subclass)
carrying `.line`, `.column`, and `.message`. A caller embedding one of
these values inside a larger document -- a config file, a template --
can report the mistake at the right spot without re-deriving the
position itself:

```python
try:
    limit = parse_size(raw_value)
except ParseError as err:
    print(f"{config_path}:{err.line}:{err.column}: {err.message}")
```

## Units

Sizes: `B`, `KB`/`MB`/`GB`/`TB`/`PB` (decimal, powers of 1000),
`KiB`/`MiB`/`GiB`/`TiB`/`PiB` (binary, powers of 1024). Case-insensitive.

Durations: `ns`, `us`, `ms`, `s`, `m`, `h`, `d`. Unlike sizes, the unit
is mandatory -- a bare `5` is ambiguous, so it's rejected rather than
guessed at. Segments can be chained into a compound literal, largest
unit first and with no space between them: `1h30m20s`. Units must
strictly decrease and none may repeat, so `1m1h` and `1h1h` are both
rejected. A single leading `-` negates the whole literal (`-1h30m`);
`format_duration` mirrors it back the same way (`-1.50h`). The `Duration`
value type stays non-negative, so it only ever sees the unsigned side of
`parse_duration`.

## Status

Early, API surface still settling. Tests live in `tests/` and run with
`python -m unittest discover`.

## Install

No package published yet. Copy the `sizetime/` directory into your
project, or point your dependency manager at this repository.

## License

MIT, see LICENSE.
