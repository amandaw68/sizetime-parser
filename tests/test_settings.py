import unittest

from sizetime import ParseError, parse_duration, parse_settings, parse_size


class ParseSettingsTests(unittest.TestCase):
    def test_basic_colon_and_equals_separators(self):
        result = parse_settings(
            "max_upload_size: 50MB\npoll_interval = 200ms\n",
            {"max_upload_size": parse_size, "poll_interval": parse_duration},
        )
        self.assertEqual(result, {"max_upload_size": 50_000_000, "poll_interval": 0.2})

    def test_blank_lines_and_comments_are_ignored(self):
        result = parse_settings(
            "\n# a comment\n  \nlimit: 10\n",
            {"limit": parse_size},
        )
        self.assertEqual(result, {"limit": 10})

    def test_key_and_value_whitespace_is_trimmed(self):
        result = parse_settings("  limit  :   10  \n", {"limit": parse_size})
        self.assertEqual(result, {"limit": 10})

    def test_empty_schema_is_an_error(self):
        with self.assertRaises(ValueError):
            parse_settings("limit: 10\n", {})

    def test_missing_separator(self):
        with self.assertRaises(ParseError) as ctx:
            parse_settings("limit 10\n", {"limit": parse_size})
        self.assertIn("expected 'key: value'", ctx.exception.message)
        self.assertEqual(ctx.exception.offset, 0)

    def test_unknown_key(self):
        with self.assertRaises(ParseError) as ctx:
            parse_settings("bogus: 10\n", {"limit": parse_size})
        self.assertIn("unknown setting 'bogus'", ctx.exception.message)

    def test_repeated_key(self):
        with self.assertRaises(ParseError) as ctx:
            parse_settings("limit: 10\nlimit: 20\n", {"limit": parse_size})
        self.assertIn("repeated", ctx.exception.message)
        self.assertEqual(ctx.exception.line, 2)

    def test_missing_value(self):
        with self.assertRaises(ParseError) as ctx:
            parse_settings("limit:\n", {"limit": parse_size})
        self.assertIn("missing value for 'limit'", ctx.exception.message)

    def test_missing_required_setting(self):
        with self.assertRaises(ParseError) as ctx:
            parse_settings("limit: 10\n", {"limit": parse_size, "interval": parse_duration})
        self.assertIn("missing required setting(s): interval", ctx.exception.message)

    def test_value_parse_error_points_at_the_right_line_and_column(self):
        text = "limit: 10MB\ninterval: 5x\n"
        with self.assertRaises(ParseError) as ctx:
            parse_settings(text, {"limit": parse_size, "interval": parse_duration})
        self.assertEqual(ctx.exception.line, 2)
        # "interval: 5x" -> the 'x' is at column 12 on line 2
        self.assertEqual(ctx.exception.column, 12)

    def test_last_line_without_trailing_newline_is_still_parsed(self):
        result = parse_settings("limit: 10", {"limit": parse_size})
        self.assertEqual(result, {"limit": 10})


if __name__ == "__main__":
    unittest.main()
