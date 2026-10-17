#!/usr/bin/env python3
"""
Content-addressed, resumable model-call cache (FR-018, research R10).

    key  = sha256(canonical_json({backend, model, effort,
                                  system_prompt_sha256, prompt_sha256, attempt}))
    path = runs/<run_id>/calls/<key[:2]>/<key>.json

- A call runs only when no record exists at its key.
- Writes are atomic (temp file in the same directory, then ``os.replace``),
  so a crash never leaves a half-written record that looks like a hit. Temp
  files start with a dot and are never read.
- Only ``outcome == "ok"`` records are reused as results. A failed attempt
  stays on disk for provenance; the next attempt has ``attempt + 1`` and so a
  new key. A rerun therefore repeats neither finished successes nor finished
  failures.

No network. No model calls: the caller passes the function that makes the
call.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Callable

from bench import records
from bench.records import canonical_json_bytes

KEY_FIELDS = ("backend", "model", "effort", "system_prompt_sha256", "prompt_sha256")
_KEY_RE = re.compile(r"^[0-9a-f]{64}$")


def call_key(*, backend: str, model: str, effort: str | None,
             system_prompt_sha256: str | None, prompt_sha256: str, attempt: int) -> str:
    payload = {
        "backend": backend,
        "model": model,
        "effort": effort,
        "system_prompt_sha256": system_prompt_sha256,
        "prompt_sha256": prompt_sha256,
        "attempt": attempt,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


class CallCache:
    """The ``calls/`` directory of one run."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def path(self, key: str) -> Path:
        return self.root / key[:2] / f"{key}.json"

    def load(self, key: str) -> dict | None:
        """Any finished record at `key` (ok or failed), or None. A missing or
        unreadable file is None."""
        p = self.path(key)
        if not p.is_file():
            return None
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        if not isinstance(rec, dict) or rec.get("key") != key:
            return None
        return rec

    def get(self, key: str) -> dict | None:
        """A reusable (``outcome == "ok"``) record at `key`, or None."""
        rec = self.load(key)
        return rec if rec is not None and rec.get("outcome") == "ok" else None

    def put(self, record: dict) -> Path:
        key = record.get("key")
        if not isinstance(key, str) or not _KEY_RE.match(key):
            raise ValueError(f"call record has no valid key: {key!r}")
        p = self.path(key)
        records.write_json(p, record)
        return p

    def run_attempts(
        self,
        spec: dict,
        call_fn: Callable[[dict, str], dict],
        max_attempts: int,
        stop_outcomes: frozenset[str] | set[str] = frozenset(),
        first_attempt: int = 1,
    ) -> dict | None:
        """Runs attempts ``first_attempt..max_attempts`` of one logical call.

        For each attempt: an existing ok record is returned without a call;
        an existing failed record is skipped (kept for provenance); a missing
        record is produced by ``call_fn(spec_with_attempt, key)``, written,
        and returned if ok. An outcome in `stop_outcomes` (for example
        ``model_policy_violation``) ends the loop at once. Returns the last
        record seen, or None when no attempt ran."""
        last = None
        for attempt in range(first_attempt, max_attempts + 1):
            spec_a = {**{f: spec.get(f) for f in KEY_FIELDS}, "attempt": attempt}
            key = call_key(**spec_a)
            existing = self.load(key)
            if existing is not None:
                last = existing
                if existing.get("outcome") == "ok" or existing.get("outcome") in stop_outcomes:
                    return existing
                continue
            rec = call_fn(spec_a, key)
            if rec.get("key") != key:
                raise ValueError("call_fn returned a record with a different key")
            self.put(rec)
            last = rec
            if rec.get("outcome") == "ok" or rec.get("outcome") in stop_outcomes:
                return rec
        return last
