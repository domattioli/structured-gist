"""Content-addressed call cache (tasks T007, FR-018, research R10)."""
from __future__ import annotations

import hashlib
import json
import subprocess

import pytest

from corpus_lib import canonical_json_bytes
from bench import cache

SPEC = {
    "backend": "claude-isolated-config",
    "model": "claude-opus-5-5",
    "effort": "medium",
    "system_prompt_sha256": "a" * 64,
    "prompt_sha256": "b" * 64,
}


def _record(key: str, outcome: str = "ok", attempt: int = 1) -> dict:
    return {
        "key": key,
        "backend": SPEC["backend"],
        "model_requested": SPEC["model"],
        "model_resolved": SPEC["model"],
        "effort": SPEC["effort"],
        "prompt_sha256": SPEC["prompt_sha256"],
        "system_prompt_sha256": SPEC["system_prompt_sha256"],
        "attempt": attempt,
        "started_at": "2026-09-27T00:00:00+00:00",
        "finished_at": "2026-09-27T00:00:01+00:00",
        "outcome": outcome,
        "tokens": {"input": 1, "output": 1, "source": "reported"},
    }


def test_key_formula():
    expected = hashlib.sha256(canonical_json_bytes({**SPEC, "attempt": 1})).hexdigest()
    assert cache.call_key(attempt=1, **SPEC) == expected


def test_attempt_changes_key():
    assert cache.call_key(attempt=1, **SPEC) != cache.call_key(attempt=2, **SPEC)


def test_key_ignores_nothing_in_spec():
    k = cache.call_key(attempt=1, **SPEC)
    for field in SPEC:
        changed = dict(SPEC)
        changed[field] = "x"
        assert cache.call_key(attempt=1, **changed) != k, field


def test_path_layout(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k = cache.call_key(attempt=1, **SPEC)
    assert c.path(k) == tmp_path / "calls" / k[:2] / f"{k}.json"


def test_write_is_atomic_and_canonical(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k = cache.call_key(attempt=1, **SPEC)
    rec = _record(k)
    c.put(rec)
    assert c.path(k).read_bytes() == canonical_json_bytes(rec)
    # No temp files left behind.
    assert [p.name for p in c.path(k).parent.iterdir()] == [f"{k}.json"]


def test_leftover_temp_file_is_never_a_hit(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k = cache.call_key(attempt=1, **SPEC)
    d = c.path(k).parent
    d.mkdir(parents=True)
    # Simulate a crash mid-write: a complete-looking temp file, no final file.
    (d / f".{k}.json.tmp-crash").write_bytes(canonical_json_bytes(_record(k)))
    assert c.get(k) is None
    assert c.load(k) is None


def test_only_ok_records_are_reused(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k1 = cache.call_key(attempt=1, **SPEC)
    c.put(_record(k1, outcome="transient_error"))
    assert c.get(k1) is None  # failed attempt is not a hit
    assert c.load(k1)["outcome"] == "transient_error"  # provenance kept
    k2 = cache.call_key(attempt=2, **SPEC)
    c.put(_record(k2, outcome="ok", attempt=2))
    assert c.get(k2)["outcome"] == "ok"


def test_put_rejects_key_mismatch(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    with pytest.raises(ValueError):
        c.put(_record("0" * 64) | {"key": "not-a-key"})


def _fake_call_fn(spec_attempt: dict, key: str) -> dict:
    proc = subprocess.run(["fake-model-cli", "--attempt", str(spec_attempt["attempt"])],
                          capture_output=True, text=True)
    outcome = "ok" if proc.returncode == 0 else "transient_error"
    return _record(key, outcome=outcome, attempt=spec_attempt["attempt"])


def test_second_pass_makes_zero_calls(tmp_path, fake_run):
    c = cache.CallCache(tmp_path / "calls")
    first = c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)
    assert first["outcome"] == "ok"
    assert len(fake_run.calls) == 1
    second = c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)
    assert second == first
    assert len(fake_run.calls) == 1  # zero new subprocess calls


def test_failed_attempt_is_kept_and_next_attempt_gets_new_key(tmp_path, fake_run):
    c = cache.CallCache(tmp_path / "calls")
    fake_run.queue(returncode=1)  # attempt 1 fails
    fake_run.queue(returncode=0)  # attempt 2 succeeds
    rec = c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)
    assert rec["attempt"] == 2 and rec["outcome"] == "ok"
    k1 = cache.call_key(attempt=1, **SPEC)
    assert c.load(k1)["outcome"] == "transient_error"
    # A resume repeats neither the failed attempt nor the successful one.
    n = len(fake_run.calls)
    assert c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)["attempt"] == 2
    assert len(fake_run.calls) == n


def test_run_attempts_gives_up_after_max(tmp_path, fake_run):
    c = cache.CallCache(tmp_path / "calls")
    for _ in range(3):
        fake_run.queue(returncode=1)
    rec = c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)
    assert rec["outcome"] == "transient_error" and rec["attempt"] == 3
    assert len(fake_run.calls) == 3
    # A rerun does not repeat finished (failed) attempts either.
    assert c.run_attempts(SPEC, _fake_call_fn, max_attempts=3)["attempt"] == 3
    assert len(fake_run.calls) == 3


def test_stop_outcome_ends_attempts(tmp_path, fake_run):
    c = cache.CallCache(tmp_path / "calls")

    def fn(spec_attempt, key):
        subprocess.run(["fake-model-cli"])
        return _record(key, outcome="model_policy_violation", attempt=spec_attempt["attempt"])

    rec = c.run_attempts(SPEC, fn, max_attempts=3, stop_outcomes={"model_policy_violation"})
    assert rec["outcome"] == "model_policy_violation"
    assert len(fake_run.calls) == 1


def test_corrupt_final_file_is_not_a_hit(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k = cache.call_key(attempt=1, **SPEC)
    c.path(k).parent.mkdir(parents=True)
    c.path(k).write_text("{not json", encoding="utf-8")
    assert c.get(k) is None


def test_json_roundtrip(tmp_path):
    c = cache.CallCache(tmp_path / "calls")
    k = cache.call_key(attempt=1, **SPEC)
    rec = _record(k)
    c.put(rec)
    assert json.loads(c.path(k).read_text(encoding="utf-8")) == rec
