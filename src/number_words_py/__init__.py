"""Public API for number_words_py.

Only the names re-exported here are considered stable. Importing from
``number_words_py.core`` directly is allowed but not part of the documented
surface.
"""

from .core import (
    NumberWordsError,
    int_to_words,
    words_to_int,
)

__all__ = [
    "NumberWordsError",
    "int_to_words",
    "words_to_int",
]

__version__ = "1.0.0"
