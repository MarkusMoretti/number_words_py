# number_words_py

Render integers as English words and parse those words back into integers.

```python
from number_words_py import int_to_words, words_to_int

int_to_words(115)
# 'one hundred fifteen'

int_to_words(-1234)
# 'negative one thousand two hundred thirty-four'

words_to_int("one hundred and five")
# 105
```

## Why this exists

The hard part of spelling numbers is not the big scales; it is the teens.
`11` is "eleven", not "ten-one", and `15` is "fifteen", not "fiveteen".
Libraries that build words digit by digit get these wrong or special-case them
badly. This library keeps a single lookup table for `0..19` and only composes
above that, so the awkward cases fall out of the data instead of out of
control flow.

The trade-off: we cover a fixed range, `[-10**21 + 1, 10**21 - 1]`. Beyond
that we raise `NumberWordsError` rather than inventing a scale name. A wrong
name that looks plausible is worse than a clear refusal.

## The edge you will hit

British English says "one hundred and five"; American English says "one
hundred five". We emit the American form, because it is the shorter and more
regular rule, but `words_to_int` accepts both. Commas, hyphens, and the
archaic "fourty" spelling are also accepted on input. Output is always
lowercase, hyphenated between tens and units (`twenty-one`), and space
separated otherwise.

## API

- `int_to_words(value: int) -> str`
- `words_to_int(text: str) -> int`
- `NumberWordsError` — a subclass of `ValueError`, raised for unsupported
  values, non-integer input, unknown words, and malformed phrases.

`int_to_words` and `words_to_int` are exact inverses over the supported range.

## Tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
