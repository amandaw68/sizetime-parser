import unittest

from sizetime import ParseError


class ParseErrorTests(unittest.TestCase):
    def test_locates_offset_on_first_line(self):
        err = ParseError("boom", "abcdef", 3, "<string>")
        self.assertEqual((err.line, err.column), (1, 4))

    def test_locates_offset_on_later_line(self):
        source = "first\nsecond\nthird"
        # offset 9 is the 'o' in "second" (line 2, index 3 within that line)
        err = ParseError("boom", source, 9, "<string>")
        self.assertEqual((err.line, err.column), (2, 4))
        self.assertEqual(err._line_text, "second")

    def test_offset_at_start_of_line_is_column_one(self):
        source = "first\nsecond"
        err = ParseError("boom", source, 6, "<string>")
        self.assertEqual((err.line, err.column), (2, 1))

    def test_offset_at_end_of_source_is_valid(self):
        source = "abc"
        err = ParseError("boom", source, 3, "<string>")
        self.assertEqual((err.line, err.column), (1, 4))

    def test_offset_past_end_of_source_is_rejected(self):
        with self.assertRaises(ValueError):
            ParseError("boom", "abc", 4, "<string>")

    def test_negative_offset_is_rejected(self):
        with self.assertRaises(ValueError):
            ParseError("boom", "abc", -1, "<string>")

    def test_render_includes_source_name_line_column_and_caret(self):
        err = ParseError("bad thing", "abcdef", 2, "myfile")
        rendered = str(err)
        lines = rendered.splitlines()
        self.assertEqual(lines[0], "myfile:1:3: bad thing")
        self.assertIn("abcdef", lines[1])
        self.assertTrue(lines[2].endswith("^"))
        self.assertEqual(lines[2].index("^") - lines[1].index("a"), 2)

    def test_is_a_value_error(self):
        self.assertIsInstance(ParseError("boom", "abc", 0, "<string>"), ValueError)


if __name__ == "__main__":
    unittest.main()
