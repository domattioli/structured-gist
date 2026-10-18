#!/usr/bin/env python3
"""
Model-free baselines and the whole-word trim (research R4, R5).

- ``word_ends`` / ``trim_to_words``: positions of counted words under the
  ``alnum-token-v2`` rule, so a text can be cut after its k-th counted word.
- ``lead_n``: the first N words of the source.
- ``textrank``: sentence TextRank (damping, tolerance, max iterations from
  prereg; stopword list from ``bench/stopwords.txt``; ties by source
  position), top sentences taken until at least N words, then trimmed to the
  band.

No network. No model calls.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from bench import words

_TOKEN = re.compile(r"\S+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD = re.compile(r"\w+", re.UNICODE)


def word_ends(text: str) -> list[int]:
    """End offsets (in `text`) of every counted word, in order. `text` must
    already be free of HTML comments."""
    ends: list[int] = []
    pos = 0
    for line in text.split("\n"):
        leading = True
        for m in _TOKEN.finditer(line):
            tok = words._EMPHASIS.sub("", m.group(0))
            if not tok:
                continue
            if leading and words.is_label(tok):
                continue
            leading = False
            if words._has_alnum(tok):
                ends.append(pos + m.end())
        pos += len(line) + 1
    return ends


def trim_to_words(text: str, limit: int) -> str:
    """Cut `text` (comments removed) after its `limit`-th counted word."""
    text = words.strip_html_comments(text)
    ends = word_ends(text)
    if len(ends) <= limit:
        return text
    return text[: ends[limit - 1]].rstrip()


def lead_n(source: str, n: int) -> str:
    text = words.strip_html_comments(source)
    ends = word_ends(text)
    if len(ends) <= n:
        return text.strip()
    return text[: ends[n - 1]].strip()


def load_stopwords(path: Path) -> frozenset[str]:
    return frozenset(w.strip().lower() for w in Path(path).read_text(encoding="utf-8").splitlines() if w.strip())


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]


def _sig_words(sentence: str, stop: frozenset[str]) -> set[str]:
    return {w for w in (x.lower() for x in _WORD.findall(sentence)) if w not in stop}


def rank_sentences(sentences: list[str], stop: frozenset[str], damping: float, tol: float,
                   max_iter: int) -> list[float]:
    n = len(sentences)
    if n == 0:
        return []
    ws = [_sig_words(s, stop) for s in sentences]
    index: dict[str, list[int]] = {}
    for i, w in enumerate(ws):
        for t in w:
            index.setdefault(t, []).append(i)
    nbrs: list[dict[int, float]] = [dict() for _ in range(n)]
    for i in range(n):
        if len(ws[i]) <= 1:
            continue
        cand = {j for t in ws[i] for j in index[t] if j > i}
        for j in cand:
            if len(ws[j]) > 1:
                common = len(ws[i] & ws[j])
                v = common / (math.log(len(ws[i])) + math.log(len(ws[j])))
                if v:
                    nbrs[i][j] = v
                    nbrs[j][i] = v
    out_sum = [sum(d.values()) for d in nbrs]
    score = [1.0 / n] * n
    for _ in range(max_iter):
        new = []
        for i in range(n):
            acc = 0.0
            for j, w in nbrs[i].items():
                if out_sum[j]:
                    acc += w / out_sum[j] * score[j]
            new.append((1 - damping) / n + damping * acc)
        delta = max(abs(a - b) for a, b in zip(new, score))
        score = new
        if delta < tol:
            break
    return score


def textrank(source: str, n: int, lo: int, hi: int, stop: frozenset[str], *, damping: float = 0.85,
             tol: float = 1e-6, max_iter: int = 200) -> str:
    text = words.strip_html_comments(source)
    if words.count_words(text) < lo:
        return text.strip()
    sentences = split_sentences(text)
    score = rank_sentences(sentences, stop, damping, tol, max_iter)
    order = sorted(range(len(sentences)), key=lambda i: (-score[i], i))
    chosen: list[int] = []
    out = ""
    for i in order:
        chosen.append(i)
        out = " ".join(sentences[k] for k in sorted(chosen))
        if words.count_words(out) >= n:
            break
    if words.count_words(out) > hi:
        out = trim_to_words(out, hi)
    return out
