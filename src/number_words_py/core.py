"""Render integers as English words and parse them back.

Design decisions worth stating up front, because they are the places where
reasonable people disagree:

* We use the short scale (US/UK modern): 10**9 is "one billion".
* Zero is "zero". Negative numbers are prefixed with "negative".
* We do not insert commas or "and". British English inserts "and" between
the hundreds and the tens ("one hundred and five"); American English does
not. We pick the American form because it is the shorter, more regular
rule, and we accept both on the way in.
* Parsing is the exact inverse of formatting for every value we format.
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "NumberWordsError",
    "int_to_words",
    "words_to_int",
]


class NumberWordsError(ValueError):
    """Raised when a value cannot be rendered or parsed.

    Subclassing ``ValueError`` means callers who only care that the input
    was bad can catch the builtin, while callers who want to distinguish
    this library's failures can catch the specific class.
    """


_ONES: Final[tuple[str, ...]] = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)

_TENS: Final[tuple[str, ...]] = (
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)

# Short-scale group names, indexed by group number where group 0 is the
# units group (1..999), group 1 is thousands, group 2 is millions, etc.
_SCALES: Final[tuple[str, ...]] = (
    "",
    "thousand",
    "million",
    "billion",
    "trillion",
    "quadrillion",
    "quintillion",
)

# The largest value we can name with the scale table above. 10**21 is the
# first number needing "sextillion", which we deliberately do not support:
# silently emitting a wrong name is worse than refusing.
_MAX: Final[int] = 10 ** (3 * len(_SCALES)) - 1
_MIN: Final[int] = -_MAX


def _three_digits_to_words(n: int) -> str:
    """Render 1..999. Caller guarantees the range."""
    parts: list[str] = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        parts.append(_ONES[hundreds])
        parts.append("hundred")
    if rest:
        if rest < 20:
            parts.append(_ONES[rest])
        else:
            tens, ones = divmod(rest, 10)
            if ones:
                parts.append(f"{_TENS[tens]}-{_ONES[ones]}")
            else:
                parts.append(_TENS[tens])
    return " ".join(parts)


def int_to_words(value: int) -> str:
    """Return the English words for ``value``.

    Supports every integer in ``[-10**21 + 1, 10**21 - 1]``. Outside that
    range a :class:`NumberWordsError` is raised rather than emitting a
    made-up scale name.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise NumberWordsError(f"expected int, got {type(value).__name__}")
    if value < _MIN or value > _MAX:
        raise NumberWordsError(
            f"value {value} is outside the supported range [{_MIN}, {_MAX}]"
        )
    if value == 0:
        return "zero"

    negative = value < 0
    n = -value if negative else value

    groups: list[str] = []
    index = 0
    while n:
        n, chunk = divmod(n, 1000)
        if chunk:
            words = _three_digits_to_words(chunk)
            if index:
                words = f"{words} {_SCALES[index]}"
            groups.append(words)
        index += 1

    # ``groups`` was built least-significant first; reverse for reading.
    result = " ".join(reversed(groups))
    if negative:
        result = f"negative {result}"
    return result


# Words that can appear in a parsed string and their numeric value. We
# accept both "forty" and the archaic "fourty" spelling because it is a
# common typo, but we never emit it.
_SMALL_WORDS: Final[dict[str, int]] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

_TENS_WORDS: Final[dict[str, int]] = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fourty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_SCALE_WORDS: Final[dict[str, int]] = {
    "thousand": 1000,
    "million": 1000 ** 2,
    "billion": 1000 ** 3,
    "trillion": 1000 ** 4,
    "quadrillion": 1000 ** 5,
    "quintillion": 1000 ** 6,
}


def _tokenize(text: str) -> list[str]:
    """Normalise input into a flat list of tokens.

    Hyphens split, commas and the word "and" are dropped. Dropping "and"
    is what lets us accept the British form even though we emit the
    American one.
    """
    lowered = text.lower()
    for ch in (",", "-"):
        lowered = lowered.replace(ch, " ")
    raw = lowered.split()
    return [tok for tok in raw if tok != "and"]


def words_to_int(text: str) -> int:
    """Parse English number words back into an :class:`int`.

    Accepts the output of :func:`int_to_words` and the common variants:
    "and" separators, commas, hyphens, and the "fourty" misspelling.
    Raises :class:`NumberWordsError` on anything else.
    """
    if not isinstance(text, str):
        raise NumberWordsError(f"expected str, got {type(text).__name__}")
    tokens = _tokenize(text)
    if not tokens:
        raise NumberWordsError("empty input")

    negative = False
    if tokens[0] == "negative":
        negative = True
        tokens = tokens[1:]
        if not tokens:
            raise NumberWordsError("dangling 'negative'")

    total = 0
    current = 0
    saw_any = False
    # Tracks the last scale used so "one thousand thousand" is rejected
    # instead of silently collapsing to a duplicate multiplier.
    last_scale = None

    for token in tokens:
        if token in _SMALL_WORDS:
            current += _SMALL_WORDS[token]
            saw_any = True
        elif token in _TENS_WORDS:
            current += _TENS_WORDS[token]
            saw_any = True
        elif token == "hundred":
            if current == 0:
                raise NumberWordsError("dangling 'hundred'")
            current *= 100
            saw_any = True
        elif token in _SCALE_WORDS:
            scale = _SCALE_WORDS[token]
            if current == 0:
                raise NumberWordsError(f"dangling '{token}'")
            if last_scale is not None and scale >= last_scale:
                raise NumberWordsError(f"misordered scale '{token}'")
            total += current * scale
            current = 0
            last_scale = scale
            saw_any = True
        else:
            raise NumberWordsError(f"unrecognised word: {token!r}")

    if not saw_any:
        raise NumberWordsError("no number words found")

    result = total + current
    if negative:
        result = -result
    if result < _MIN or result > _MAX:
        raise NumberWordsError(
            f"value {result} is outside the supported range [{_MIN}, {_MAX}]"
        )
    return result
