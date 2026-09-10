#!/usr/bin/env python3
"""
Shared deterministic text normalization for scoring/wording_fidelity.py and
scoring/findability.py. One normalizer, used identically on both "source"
and "output" text by both evals, so a wording-fidelity alignment failure and
a findability alignment failure mean the same thing (see
WORDING_FIDELITY_FINDINGS.md "Interaction with findability").

Conservative by design (see README.md pressure-check list): removes or
normalizes ONLY presentation artifacts that this corpus's renderings
actually exhibit (inspected directly -- see the case list in
WORDING_FIDELITY_FINDINGS.md "Normalization was inspected against real
renderings, not designed in the abstract"). Never stems, never fuzzy/
edit-distance-matches, never embeds. A paraphrase must still fail to match
after normalization -- that is the point of both evals.

Two representations of the same text are produced:
  - `normalize()` -> a single normalized string, case PRESERVED, for
    human-readable diagnostic display (non-verbatim nodes, novel spans).
  - `tokenize()` -> a list of tokens from that normalized string, case
    FOLDED, for the actual containment/matching arithmetic. Case-folding
    only happens at this final matching step, and only for one documented
    reason: turning a mid-sentence clause into a standalone node/line
    routinely re-capitalizes its first letter with no wording change at
    all (e.g. source "...but this repo actually keeps..." -> node "Repo
    keeps skills top-level..."). Treating that alone as a "paraphrase"
    would penalize a presentation artifact, not measure one. Every other
    letter-for-letter difference still counts.
"""
from __future__ import annotations

import re
from typing import List

_CODE_SPAN = re.compile(r"`([^`]*)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_STRIKE = re.compile(r"~~([^~]+)~~")
_UNDERLINE = re.compile(r"</?u>")
_MD_ESCAPE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!])")
_WS = re.compile(r"\s+")
# Lookahead requires the punctuation to be followed by whitespace/end (a
# real word-final mark), NOT by another character -- otherwise this would
# glue a stray space before an unrelated token that merely starts with
# punctuation, e.g. "assumed `.claude/`" -> "assumed .claude/" must NOT
# become "assumed.claude/". Caught by inspecting actual normalizer output
# against this corpus's renderings (`.claude/`-style inline-code paths are
# common here) -- see WORDING_FIDELITY_FINDINGS.md "Normalization bug
# caught before scoring: space-before-punctuation over-match".
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,;:!?])(?=\s|$)")

_QUOTE_MAP = str.maketrans({
    "‘": "'", "’": "'",   # ' '
    "“": '"', "”": '"',   # " "
    " ": " ",                    # NBSP
})

# Stripped only from a token's ENDS (str.strip semantics) -- never from the
# middle, so "top-level", "skills/<name>/SKILL.md", "it's" are untouched.
# Deliberately excludes hyphen/dash and slash: a leading/trailing "-" can be
# part of a negative number or a genuine token, and "/" is often load-
# bearing in a path. See WORDING_FIDELITY_FINDINGS.md "Why hyphens are not
# in the punctuation-strip set".
_EDGE_PUNCT = ".,;:!?()[]{}\"'"


def normalize(text: str) -> str:
    """Strip presentation-only markdown/markup artifacts and collapse
    whitespace. Case and word choice are UNTOUCHED -- this is the string
    shown in diagnostics."""
    if not text:
        return ""
    s = text.translate(_QUOTE_MAP)
    s = _CODE_SPAN.sub(r"\1", s)       # `x` -> x
    s = _BOLD.sub(r"\1", s)            # **x** -> x
    s = _ITALIC.sub(r"\1", s)          # *x* -> x
    s = _STRIKE.sub(r"\1", s)          # ~~x~~ -> x
    s = _UNDERLINE.sub("", s)          # <u>/</u> -> (removed)
    s = _MD_ESCAPE.sub(r"\1", s)       # \_ -> _  etc (markdown escaping)
    s = _WS.sub(" ", s).strip()        # collapse indentation / line-wrap whitespace
    s = _SPACE_BEFORE_PUNCT.sub(r"\1", s)  # "session ." -> "session." (wrap-rejoin artifact)
    return s


def tokenize(text: str) -> List[str]:
    """normalize() + whitespace-split + strip edge punctuation + casefold.
    Casefolding is the one lossy step -- see module docstring. Empty tokens
    (e.g. a token that was pure punctuation, like a standalone em dash) are
    dropped; they carry no wording to compare."""
    normalized = normalize(text)
    if not normalized:
        return []
    out = []
    for word in normalized.split(" "):
        w = word.strip(_EDGE_PUNCT)
        if w:
            out.append(w.lower())
    return out


_SEP = "\x01"


def contains_contiguous(needle_tokens: List[str], haystack_tokens: List[str]) -> bool:
    """True if needle_tokens appears as a contiguous, token-boundary-exact
    run inside haystack_tokens. Implemented as a separator-joined substring
    check (a token can never itself contain \\x01), which is exact token-
    sequence containment, not a character-level substring test."""
    if not needle_tokens:
        return False
    needle = _SEP + _SEP.join(needle_tokens) + _SEP
    haystack = _SEP + _SEP.join(haystack_tokens) + _SEP
    return needle in haystack


def longest_contiguous_match_len(tokens: List[str], start: int, haystack_tokens: List[str]) -> int:
    """Longest L such that tokens[start:start+L] is a contiguous run inside
    haystack_tokens. Binary search over L is valid because containment is
    monotonic in L: if tokens[start:start+L] occurs verbatim in the
    haystack at some offset k, then tokens[start:start+L'] for any L' < L
    equals haystack[k:k+L'], i.e. it is also a substring occurrence -- so
    the set of matching lengths starting at `start` is exactly {0, 1, ...,
    L_max}, never a gap in the middle."""
    max_possible = len(tokens) - start
    if max_possible <= 0:
        return 0
    lo, hi = 0, max_possible
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if contains_contiguous(tokens[start:start + mid], haystack_tokens):
            lo = mid
        else:
            hi = mid - 1
    return lo
