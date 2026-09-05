import unittest

from sizetime import ParseError, format_duration, parse_duration


class ParseDurationTests(unittest.TestCase):
    def test_simple_units(self):
        self.assertEqual(parse_duration("500ms"), 0.5)
        self.assertEqual(parse_duration("2.5s"), 2.5)
        self.assertEqual(parse_duration("90m"), 5400.0)
        self.assertEqual(parse_duration("3h"), 10800.0)
        self.assertEqual(parse_duration("1d"), 86400.0)
        self.assertEqual(parse_duration("1ns"), 1e-9)
        self.assertEqual(parse_duration("1us"), 1e-6)

    def test_compound_literal(self):
        self.assertEqual(parse_duration("1h30m20s"), 5420.0)
        self.assertEqual(parse_duration("1d2h"), 86400.0 + 2 * 3600.0)

    def test_case_insensitive_unit(self):
        self.assertEqual(parse_duration("1H"), parse_duration("1h"))

    def test_surrounding_and_internal_whitespace_is_ignored(self):
        self.assertEqual(parse_duration("  1h  "), 3600.0)
        self.assertEqual(parse_duration("1 h"), 3600.0)

    def test_empty_string_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("")
        self.assertEqual(ctx.exception.offset, 0)

    def test_whitespace_only_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("   ")
        self.assertEqual(ctx.exception.offset, 0)

    def test_bare_number_is_rejected(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("5")
        self.assertIn("missing time unit", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 1)

    def test_unknown_unit(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("5x")
        self.assertIn("unknown time unit", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 1)

    def test_repeated_unit_is_rejected(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("1h1h")
        self.assertIn("repeated", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 3)

    def test_out_of_order_units_rejected(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("1m1h")
        self.assertIn("out of order", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 3)

    def test_equal_unit_repeated_across_segments_is_rejected_as_repeat(self):
        # same unit twice hits the "repeated" check before "out of order",
        # since equal units aren't strictly decreasing either
        with self.assertRaises(ParseError) as ctx:
            parse_duration("1s1s")
        self.assertIn("repeated", ctx.exception.message)

    def test_trailing_garbage_after_valid_literal(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("5s extra")
        self.assertEqual(ctx.exception.offset, 3)

    def test_malformed_number(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("abcs")
        self.assertEqual(ctx.exception.offset, 0)

    def test_negative_sign(self):
        self.assertEqual(parse_duration("-5s"), -5.0)
        self.assertEqual(parse_duration("-1h30m"), -5400.0)

    def test_negative_sign_after_leading_whitespace(self):
        self.assertEqual(parse_duration("  -5s"), -5.0)

    def test_negative_zero_is_zero(self):
        self.assertEqual(parse_duration("-0s"), 0.0)

    def test_bare_sign_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("-")
        self.assertIn("expected a number", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 1)

    def test_double_sign_is_an_error(self):
        with self.assertRaises(ParseError) as ctx:
            parse_duration("--5s")
        self.assertIn("expected a number", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 1)

    def test_sign_may_not_repeat_per_segment(self):
        # the sign only applies once, up front -- a "-" before a later
        # segment is trailing garbage, not a second negation
        with self.assertRaises(ParseError) as ctx:
            parse_duration("-1h-30m")
        self.assertIn("unexpected text", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 3)

    def test_error_message_is_self_contained(self):
        try:
            parse_duration("1m1h")
        except ParseError as err:
            rendered = str(err)
        self.assertIn("1m1h", rendered)
        self.assertIn("^", rendered)


class FormatDurationTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_duration(0), "0s")

    def test_picks_largest_unit_that_keeps_value_at_least_one(self):
        self.assertEqual(format_duration(90), "1.50m")
        self.assertEqual(format_duration(59), "59.00s")
        self.assertEqual(format_duration(60), "1.00m")

    def test_falls_back_to_smaller_units_for_small_values(self):
        self.assertEqual(format_duration(0.5), "500.00ms")

    def test_falls_back_to_nanoseconds_below_microsecond(self):
        self.assertEqual(format_duration(5e-10), "0.50ns")

    def test_negative_gets_a_leading_sign(self):
        self.assertEqual(format_duration(-90), "-1.50m")
        self.assertEqual(format_duration(-0.5), "-500.00ms")

    def test_negative_zero_formats_as_zero(self):
        self.assertEqual(format_duration(-0.0), "0s")

    def test_round_trips_through_parse_duration(self):
        self.assertEqual(format_duration(parse_duration("-1h30m")), "-1.50h")


if __name__ == "__main__":
    unittest.main()
