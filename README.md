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

format_size(1_500_000)                # -> "1.5MB"
format_size(1_500_000, binary=True)   # -> "1.4MiB"
format_duration(90)                   # -> "1.50m"
```

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
guessed at.

## Status

Early. Compound durations (`1h30m20s`) aren't supported yet -- see the
roadmap below.

## Install

No package published yet. Copy the `sizetime/` directory into your
project, or point your dependency manager at this repository.

## License

MIT, see LICENSE.
