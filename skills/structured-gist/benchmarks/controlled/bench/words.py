#!/usr/bin/env python3
"""
Benchmark word counter, rule name ``alnum-token-v2`` (research R4, FR-006).

One counter is used for all five methods:

1. HTML comments (``<!-- ... -->``, possibly spanning lines) are removed.
2. ``**``, ``__`` and backticks are removed.
3. On every line, leading list-label tokens are stripped, repeatedly while
   the first remaining token is a label: bullet markers ``-`` ``*`` ``+``,
   enumerator labels matching ``^([IVXLC]+|[ivxlc]+|[A-Z]|[a-z]|\\d+)\\.$``,
   and the block glyphs ``▸`` and ``↪``. So ``- I. item`` counts 1.
4. A word is a whitespace-delimited token that contains at least one Unicode
   alphanumeric character. Bare punctuation, ``#`` and dashes do not count.

The linter's ``count_words`` (skills/structured-gist/tests/lint_outline.py)
counts list dashes, so it is reported only as a diagnostic.

No network. No model calls.
"""
from __future__ import annotations

import re

COUNTER_NAME = "alnum-token-v2"

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_EMPHASIS = re.compile(r"\*\*|__|`")
_ENUM_LABEL = re.compile(r"^([IVXLC]+|[ivxlc]+|[A-Z]|[a-z]|\d+)\.$")
_BULLETS = frozenset({"-", "*", "+"})
_GLYPHS = frozenset({"▸", "↪"})


def strip_html_comments(text: str) -> str:
    """Removes every HTML comment, including multi-line ones."""
    return _HTML_COMMENT.sub("", text)


def is_label(token: str) -> bool:
    """True when `token` is a list label that is stripped at line start."""
    return token in _BULLETS or token in _GLYPHS or bool(_ENUM_LABEL.match(token))


def _has_alnum(token: str) -> bool:
    return any(ch.isalnum() for ch in token)


def line_tokens(line: str) -> list[str]:
    """Whitespace tokens of one line after emphasis removal and leading
    label stripping (HTML comments must already be removed)."""
    tokens = _EMPHASIS.sub("", line).split()
    i = 0
    while i < len(tokens) and is_label(tokens[i]):
        i += 1
    return tokens[i:]


def word_tokens(text: str) -> list[str]:
    """Every counted word of `text`, in order."""
    out: list[str] = []
    for line in strip_html_comments(text).split("\n"):
        out.extend(t for t in line_tokens(line) if _has_alnum(t))
    return out


def count_words(text: str) -> int:
    """The ``alnum-token-v2`` word count of `text`."""
    return len(word_tokens(text))
