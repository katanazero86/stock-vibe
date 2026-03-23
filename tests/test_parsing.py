from math import isclose
import unittest

from stock_vibe.parsing import parse_compact_number, parse_percent


class ParsingTests(unittest.TestCase):
    def test_parse_compact_number_with_suffix(self) -> None:
        self.assertTrue(isclose(parse_compact_number("41.68 B USD"), 41.68 * 1_000_000_000))

    def test_parse_percent_with_unicode_minus(self) -> None:
        self.assertTrue(isclose(parse_percent("−3.28%"), -3.28))


if __name__ == "__main__":
    unittest.main()
