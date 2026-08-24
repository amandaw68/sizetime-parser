import unittest

from sizetime import ParseError, format_size, parse_size


class ParseSizeTests(unittest.TestCase):
    def test_bare_number_is_bytes(self):
        self.assertEqual(parse_size("100"), 100)

    def test_decimal_units(self):
        self.assertEqual(parse_size("512KB"), 512_000)
        self.assertEqual(parse_size("1MB"), 1_000_000)
        self.assertEqual(parse_size("1GB"), 1_000_000_000)
        self.assertEqual(parse_size("1TB"), 1_000_000_000_000)
        self.assertEqual(parse_size("1PB"), 1_000_000_000_000_000)

    def test_binary_units(self):
        self.assertEqual(parse_size("1KiB"), 1024)
        self.assertEqual(parse_size("1MiB"), 1024**2)
        self.assertEqual(parse_size("1GiB"), 1024**3)

    def test_case_insensitive(self):
        self.assertEqual(parse_size("10mb"), parse_size("10MB"))
        self.assertEqual(parse_size("10gib"), parse_size("10GiB"))

    def test_fractional_amount(self):
        self.assertEqual(parse_size("1.5GiB"), round(1.5 * 1024**3))

    def test_space_between_number_and_unit(self):
        self.assertEqual(parse_size("10 MB"), 10_000_000)

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(parse_size("  100  "), 100)

    def test_rounds_to_nearest_byte(self):
        self.assertEqual(parse_size("1.0000001KB"), 1000)

    def test_empty_string_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("")
        self.assertEqual(ctx.exception.offset, 0)

    def test_whitespace_only_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("   ")
        self.assertEqual(ctx.exception.offset, 0)

    def test_missing_number(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("MB")
        self.assertEqual(ctx.exception.offset, 0)

    def test_garbage_number(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("--5MB")
        self.assertEqual(ctx.exception.offset, 0)

    def test_unknown_unit(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("50 MG")
        self.assertEqual(ctx.exception.offset, 3)
        self.assertEqual(ctx.exception.column, 4)

    def test_unit_glued_to_trailing_garbage_is_one_unknown_unit(self):
        # the unit regex is greedy, so "MBextra" is parsed and rejected as
        # a single unknown unit rather than "MB" plus leftover text
        with self.assertRaises(ParseError) as ctx:
            parse_size("10MBextra")
        self.assertEqual(ctx.exception.offset, 2)

    def test_trailing_garbage_after_valid_literal(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("10MB extra")
        self.assertEqual(ctx.exception.offset, 5)

    def test_error_message_is_self_contained(self):
        try:
            parse_size("50 MG")
        except ParseError as err:
            rendered = str(err)
        self.assertIn("50 MG", rendered)
        self.assertIn("^", rendered)
        self.assertIn("unknown size unit", rendered)

    def test_source_name_is_used_in_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_size("bad", source_name="app.conf")
        self.assertIn("app.conf:1:1", str(ctx.exception))


class FormatSizeTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_size(0), "0B")

    def test_bytes_stay_bytes_below_base(self):
        self.assertEqual(format_size(999), "999B")

    def test_decimal_rollover(self):
        self.assertEqual(format_size(1_500_000), "1.5MB")

    def test_binary_rollover(self):
        self.assertEqual(format_size(1_500_000, binary=True), "1.4MiB")

    def test_negative_is_an_error(self):
        with self.assertRaises(ValueError):
            format_size(-1)

    def test_round_trips_at_low_end(self):
        # below the first unit boundary, format_size and parse_size are exact inverses
        for n in (0, 1, 999):
            self.assertEqual(parse_size(format_size(n)), n)


if __name__ == "__main__":
    unittest.main()
