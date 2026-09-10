#!/usr/bin/env python3
"""
Shared, dependency-free helpers used by select_cases.py, build_cases.py and
verify_corpus.py: deterministic hashing, deterministic ordering, and
deterministic JSON serialization. No network. No model calls.

Kept as one small module (rather than duplicated per-script) because all
three scripts must agree byte-for-byte on how a hash or an ordering key is
computed -- select_cases.py picks cases by a sha256-based order,
build_cases.py serializes the picked cases, and verify_corpus.py
recomputes both from scratch and must land on the identical values.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


BUILD_SCRIPT_VERSION = "1.0.0"


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def selection_sort_key(dataset_name: str, upstream_case_id: str) -> str:
    """The one selection-order rule every dataset's picker uses:
    sha256(dataset_name + upstream_case_id), hex. Deterministic, has no
    relationship to case "quality" or difficulty, and is trivially
    re-derivable by anyone re-running the pipeline against the same pinned
    upstream data.
    """
    return sha256_hex(f"{dataset_name}\x00{upstream_case_id}")


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic JSON serialization: sorted keys, fixed separators, a
    trailing newline, UTF-8. Two calls with equal `obj` always produce
    byte-identical output -- this is what makes case rebuilds byte-stable.
    """
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, obj: Any) -> bytes:
    data = canonical_json_bytes(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


_WORD_RE = re.compile(r"\S+")


def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))


def scarcity_first_allocate(
    availability: dict[str, int], quota_total: int, per_key_cap: int | None = None
) -> dict[str, int]:
    """Deterministically spreads `quota_total` slots across the keys of
    `availability` (key -> how many candidates exist for that key),
    processing the scarcest keys first (fewest available, ties broken by
    key name) so that scarce strata get first claim on their own
    candidates instead of being crowded out by a keyword with many. Used
    for QMSum's single/multi split across domains and Qasper's
    single/multi split across evidence-distance buckets -- same rule,
    different strata.
    """
    order = sorted(availability, key=lambda k: (availability[k], k))
    remaining = quota_total
    result = {k: 0 for k in availability}
    for k in order:
        cap = availability[k] if per_key_cap is None else min(availability[k], per_key_cap)
        take = min(remaining, cap)
        result[k] = take
        remaining -= take
    # second pass without the per-key cap, in the same scarcity order, in
    # case the cap left quota unfilled and more capacity exists.
    if remaining > 0 and per_key_cap is not None:
        for k in order:
            extra_capacity = availability[k] - result[k]
            take = min(remaining, extra_capacity)
            result[k] += take
            remaining -= take
    return result


def size_bucket(word_count_value: int, boundaries: tuple[int, ...]) -> str:
    """Assigns a size bucket label (0-indexed bucket -> 'bucket_N') given
    ascending word-count boundaries. Used to keep a spread of source sizes
    instead of implicitly favoring the shortest documents.
    """
    idx = 0
    for b in boundaries:
        if word_count_value > b:
            idx += 1
        else:
            break
    return f"bucket_{idx}"
