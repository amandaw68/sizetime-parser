import unittest

from sizetime import Duration, ParseError, Size


class SizeTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(Size.parse("1MB"), Size(1_000_000))

    def test_parse_propagates_parse_error(self):
        with self.assertRaises(ParseError):
            Size.parse("50 MG")

    def test_str_uses_format_size(self):
        self.assertEqual(str(Size(1_500_000)), "1.5MB")

    def test_repr(self):
        self.assertEqual(repr(Size(100)), "Size(100)")

    def test_negative_is_an_error(self):
        with self.assertRaises(ValueError):
            Size(-1)

    def test_equality(self):
        self.assertEqual(Size(100), Size(100))
        self.assertNotEqual(Size(100), Size(200))
        self.assertNotEqual(Size(100), 100)

    def test_hashable(self):
        self.assertEqual({Size(100), Size(100), Size(200)}, {Size(100), Size(200)})

    def test_ordering(self):
        self.assertLess(Size(100), Size(200))
        self.assertLessEqual(Size(100), Size(100))
        self.assertGreater(Size(200), Size(100))
        self.assertGreaterEqual(Size(200), Size(200))

    def test_addition(self):
        self.assertEqual(Size(100) + Size(50), Size(150))

    def test_subtraction(self):
        self.assertEqual(Size(150) - Size(50), Size(100))

    def test_subtraction_below_zero_is_an_error(self):
        with self.assertRaises(ValueError):
            Size(50) - Size(100)

    def test_multiplication_by_scalar(self):
        self.assertEqual(Size(100) * 3, Size(300))
        self.assertEqual(3 * Size(100), Size(300))
        self.assertEqual(Size(100) * 1.5, Size(150))

    def test_division_by_scalar(self):
        self.assertEqual(Size(100) / 4, Size(25))

    def test_division_by_size_gives_ratio(self):
        self.assertEqual(Size(100) / Size(50), 2.0)

    def test_comparison_with_unrelated_type_is_an_error(self):
        with self.assertRaises(TypeError):
            Size(100) < 100


class DurationTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(Duration.parse("1.5h"), Duration(5400.0))

    def test_parse_propagates_parse_error(self):
        with self.assertRaises(ParseError):
            Duration.parse("5")

    def test_str_uses_format_duration(self):
        self.assertEqual(str(Duration(90)), "1.50m")

    def test_repr(self):
        self.assertEqual(repr(Duration(1.5)), "Duration(1.5)")

    def test_negative_is_an_error(self):
        with self.assertRaises(ValueError):
            Duration(-1)

    def test_equality(self):
        self.assertEqual(Duration(60), Duration(60))
        self.assertNotEqual(Duration(60), Duration(120))
        self.assertNotEqual(Duration(60), 60)

    def test_hashable(self):
        self.assertEqual({Duration(60), Duration(60), Duration(120)}, {Duration(60), Duration(120)})

    def test_ordering(self):
        self.assertLess(Duration(60), Duration(120))
        self.assertLessEqual(Duration(60), Duration(60))
        self.assertGreater(Duration(120), Duration(60))
        self.assertGreaterEqual(Duration(120), Duration(120))

    def test_addition(self):
        self.assertEqual(Duration(60) + Duration(30), Duration(90))

    def test_subtraction(self):
        self.assertEqual(Duration(90) - Duration(30), Duration(60))

    def test_subtraction_below_zero_is_an_error(self):
        with self.assertRaises(ValueError):
            Duration(30) - Duration(90)

    def test_multiplication_by_scalar(self):
        self.assertEqual(Duration(30) * 3, Duration(90))
        self.assertEqual(3 * Duration(30), Duration(90))

    def test_division_by_scalar(self):
        self.assertEqual(Duration(90) / 3, Duration(30))

    def test_division_by_duration_gives_ratio(self):
        self.assertEqual(Duration(90) / Duration(30), 3.0)

    def test_comparison_with_unrelated_type_is_an_error(self):
        with self.assertRaises(TypeError):
            Duration(60) < 60


if __name__ == "__main__":
    unittest.main()
