"""Known-answer tests for the benchmark word counter ``alnum-token-v2``
(tasks T006, research R4, FR-006)."""
from __future__ import annotations

import pytest

import lint_outline
from bench import words


@pytest.mark.parametrize(
    "text, expected",
    [
        ("- item one", 2),
        ("- item", 1),
        ("I. item", 1),
        ("- I. item", 1),
        ("  - **Attr**", 1),
        ("A. two words", 2),
        ("ii. x", 1),
        ("**Bold** text", 2),
        ("# Title", 1),
        ("— , .", 0),
        ("naïve café", 2),
        ("<!-- source: x -->word", 1),
    ],
)
def test_known_answers(text, expected):
    assert words.count_words(text) == expected


def test_labels_stripped_only_at_line_start():
    # "I." mid-line is an ordinary token with an alphanumeric character.
    assert words.count_words("see item I. here") == 4
    # Each line gets its own label stripping.
    assert words.count_words("- a\n- b\nI. c\n  ▸ d\n    ↪ e") == 5


def test_labels_stripped_repeatedly():
    assert words.count_words("- A. i. 1. word") == 1
    assert words.count_words("+ * - word") == 1


def test_block_glyphs_are_labels():
    assert words.count_words("▸ **Cause** heat") == 2
    assert words.count_words("↪ One prose sentence here.") == 4


def test_emphasis_and_backticks_stripped():
    assert words.count_words("__under__ `code` **bold**") == 3
    assert words.count_words("`-`") == 0


def test_multiline_html_comment_removed():
    text = "<!-- a\nmulti line\ncomment -->\nkept words"
    assert words.strip_html_comments(text) == "\nkept words"
    assert words.count_words(text) == 2


def test_empty_and_whitespace():
    assert words.count_words("") == 0
    assert words.count_words("   \n\t ") == 0


def test_counter_name():
    assert words.COUNTER_NAME == "alnum-token-v2"


def test_lint_count_words_is_diagnostic_only():
    # The linter's counter counts the list dash; the benchmark counter does
    # not. This is why lint_outline.count_words is a diagnostic only (R4).
    assert lint_outline.count_words("- a") == 2
    assert words.count_words("- a") == 1
    assert lint_outline.count_words("- a") != words.count_words("- a")
