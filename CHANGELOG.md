# Changelog

## Unreleased

- `format_size` and `format_duration` no longer print a value that rounds
  up to the next unit's threshold, such as `1000.0KB` or `60.00s`; they
  use the larger unit instead (`1.0MB`, `1.00m`).

## 0.1.0

First release.

- `parse_size` / `format_size`: decimal (KB..PB) and binary (KiB..PiB) byte
  sizes, case-insensitive, bare numbers treated as bytes.
- `parse_duration` / `format_duration`: `ns` through `d`, compound literals
  like `1h30m20s`, optional leading `-`.
- `Size` and `Duration`: immutable, non-negative, comparable, hashable
  wrappers with the arithmetic you'd expect (add, subtract, scale, ratio).
- `parse_settings`: parse a whole `key: value` config file against a
  schema, with unknown/repeated/missing keys reported the same way as a
  bad value.
- `ParseError`: every failure carries `.line`, `.column`, and `.message`,
  and renders a caret pointing at the offending character.
