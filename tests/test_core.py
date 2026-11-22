"""Tests for number_words_py.

Run with ``PYTHONPATH=src python -m unittest discover -s tests``.
"""

import unittest

from number_words_py import (
    NumberWordsError,
    int_to_words,
    words_to_int,
)


class IntToWordsTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(int_to_words(0), "zero")

    def test_single_digits(self):
        self.assertEqual(int_to_words(1), "one")
        self.assertEqual(int_to_words(9), "nine")

    def test_teens(self):
        # The awkward case: 11..19 are not "ten-one" etc.
        self.assertEqual(int_to_words(11), "eleven")
        self.assertEqual(int_to_words(13), "thirteen")
        self.assertEqual(int_to_words(15), "fifteen")
        self.assertEqual(int_to_words(19), "nineteen")

    def test_exact_tens(self):
        self.assertEqual(int_to_words(20), "twenty")
        self.assertEqual(int_to_words(40), "forty")
        self.assertEqual(int_to_words(90), "ninety")

    def test_compound_tens(self):
        self.assertEqual(int_to_words(21), "twenty-one")
        self.assertEqual(int_to_words(99), "ninety-nine")

    def test_hundreds(self):
        self.assertEqual(int_to_words(100), "one hundred")
        self.assertEqual(int_to_words(105), "one hundred five")
        self.assertEqual(int_to_words(115), "one hundred fifteen")
        self.assertEqual(int_to_words(999), "nine hundred ninety-nine")

    def test_thousands(self):
        self.assertEqual(int_to_words(1000), "one thousand")
        self.assertEqual(int_to_words(1001), "one thousand one")
        self.assertEqual(int_to_words(1234), "one thousand two hundred thirty-four")

    def test_scale_boundary(self):
        self.assertEqual(int_to_words(10 ** 6), "one million")
        self.assertEqual(int_to_words(10 ** 9), "one billion")

    def test_negative(self):
        self.assertEqual(int_to_words(-1), "negative one")
        self.assertEqual(int_to_words(-42), "negative forty-two")

    def test_rejects_non_int(self):
        with self.assertRaises(NumberWordsError):
            int_to_words(1.5)
        with self.assertRaises(NumberWordsError):
            int_to_words("1")

    def test_bool_is_not_int(self):
        # bool is a subclass of int; rendering True as "one" would be a
        # surprising silent coercion.
        with self.assertRaises(NumberWordsError):
            int_to_words(True)

    def test_out_of_range(self):
        with self.assertRaises(NumberWordsError):
            int_to_words(10 ** 21)
        with self.assertRaises(NumberWordsError):
            int_to_words(-(10 ** 21))


class WordsToIntTests(unittest.TestCase):
    def test_round_trip_small(self):
        for n in (0, 1, 9, 10, 11, 19, 20, 21, 99, 100, 105, 115, 999):
            self.assertEqual(words_to_int(int_to_words(n)), n)

    def test_round_trip_large(self):
        for n in (1000, 1001, 1234, 10 ** 6, 10 ** 9, 987654321):
            self.assertEqual(words_to_int(int_to_words(n)), n)

    def test_round_trip_negative(self):
        for n in (-1, -42, -1000, -(10 ** 9)):
            self.assertEqual(words_to_int(int_to_words(n)), n)

    def test_accepts_and(self):
        # We emit the American form but accept the British one.
        self.assertEqual(words_to_int("one hundred and five"), 105)

    def test_accepts_commas_and_hyphens(self):
        self.assertEqual(words_to_int("one thousand, two hundred thirty-four"), 1234)
        self.assertEqual(words_to_int("twenty-one"), 21)

    def test_accepts_fourty(self):
        self.assertEqual(words_to_int("fourty"), 40)

    def test_case_insensitive(self):
        self.assertEqual(words_to_int("Twenty-One"), 21)

    def test_rejects_empty(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("")
        with self.assertRaises(NumberWordsError):
            words_to_int("   ")

    def test_rejects_unknown_word(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("one banana")

    def test_rejects_dangling_scale(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("thousand")
        with self.assertRaises(NumberWordsError):
            words_to_int("hundred")

    def test_rejects_misordered_scale(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("one thousand thousand")

    def test_rejects_dangling_negative(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("negative")

    def test_rejects_non_str(self):
        with self.assertRaises(NumberWordsError):
            words_to_int(42)

    def test_out_of_range(self):
        with self.assertRaises(NumberWordsError):
            words_to_int("one sextillion")


if __name__ == "__main__":
    unittest.main()
