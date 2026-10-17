"""Evals-shaped local records and the stdlib schema validator
(tasks T008, FR-016, FR-017)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from corpus_lib import canonical_json_bytes
from bench import records

H = "0123456789abcdef" * 4  # a valid sha256-shaped string


def _item(**over):
    item = {
        "item_id": "qmsum/qmsum-01",
        "dataset": "qmsum",
        "case_id": "qmsum-01",
        "source_sha256": H,
        "source_words": 100,
        "facts": [{"id": "f1", "text": "t", "category": "c", "weight": 2}],
        "relations": [{"id": "r1", "text": "t", "type": "causal", "fact_ids": ["f1", "f2"]}],
        "reference_answer": "ans",
        "question_or_query": "q?",
    }
    item.update(over)
    return item


def _sample(**over):
    s = {
        "sample_id": "qmsum/qmsum-01/plain_bullets",
        "item_id": "qmsum/qmsum-01",
        "method": "plain_bullets",
        "status": "generated",
        "output_text": "- a b",
        "words": 2,
        "n_target": 2,
        "band": [2, 2],
        "length_flags": [],
        "call_keys": [H],
    }
    s.update(over)
    return s


def _call(**over):
    c = {
        "key": H,
        "backend": "agents-inc-codex",
        "model_requested": "sol",
        "model_resolved": "gpt-5.6-sol",
        "effort": "medium",
        "prompt_sha256": H,
        "system_prompt_sha256": None,
        "attempt": 1,
        "started_at": "2026-09-27T00:00:00+00:00",
        "finished_at": "2026-09-27T00:00:01+00:00",
        "outcome": "ok",
        "tokens": {"input": 10, "output": 5, "source": "reported"},
    }
    c.update(over)
    return c


def _grader(**over):
    g = {"grader": "fact_retention.sol", "grader_type": "python",
         "sample_id": "qmsum/qmsum-01/skill", "status": "scored", "score": 0.5}
    g.update(over)
    return g


def _dataset_results(**over):
    comp = {"n_pairs": 3, "mean_diff": 0.1, "ci95": [0.0, 0.2], "p_greater": 0.125,
            "p_less": 1.0, "p_greater_holm": 0.5, "p_less_holm": 1.0, "test": "exact"}
    d = {
        "dataset": "qasper",
        "result_counts": {"total": 1, "passed": 0, "failed": 0, "errored": 0},
        "per_testing_criteria_results": [{"testing_criteria": "fact_retention.sol", "passed": 0, "failed": 0}],
        "per_model_usage": [{"model_name": "gpt-5.6-sol", "invocation_count": 1, "prompt_tokens": 1,
                             "completion_tokens": 1, "total_tokens": 2}],
        "verdicts": [{"control": "plain_bullets", "fact": comp, "relation_check_applied": False,
                      "verdict": "no difference shown", "relation": None}],
    }
    d.update(over)
    return d


VALID = [
    ("ItemLine", {"item": _item()}),
    ("Item", _item(reference_answer=None, question_or_query=None, dataset="wildchat")),
    ("Sample", _sample()),
    ("Sample", _sample(method="skill", n_target=None, band=None, call_keys=[])),
    ("CallRecord", _call()),
    ("GraderResult", _grader()),
    ("GraderResult", _grader(status="incomplete", score=None)),
    ("DatasetResults", _dataset_results()),
]

INVALID = [
    ("Item", _item(dataset="cnn")),                                # enum
    ("Item", {k: v for k, v in _item().items() if k != "facts"}),   # required
    ("Item", _item(source_words=0)),                               # minimum
    ("Item", _item(source_sha256="xyz")),                          # pattern via $ref
    ("Item", _item(facts=[{"id": "f1", "text": "t", "category": "c", "weight": 4}])),  # maximum
    ("Item", _item(extra=1)),                                      # additionalProperties
    ("ItemLine", {"item": _item(), "x": 1}),
    ("Sample", _sample(method="lead-n")),
    ("Sample", _sample(words=-1)),
    ("Sample", _sample(band=[1, 2, 3])),                           # maxItems
    ("Sample", _sample(length_flags=["too_long"])),
    ("Sample", _sample(words=True)),                               # bool is not an integer
    ("CallRecord", _call(outcome="maybe")),
    ("CallRecord", _call(attempt=0)),
    ("CallRecord", _call(tokens={"input": 1, "output": 1})),        # nested required
    ("CallRecord", _call(error_text="x" * 601)),                   # maxLength
    ("GraderResult", _grader(grader_type="multi")),
    ("GraderResult", _grader(status="passed")),
    ("DatasetResults", _dataset_results(verdicts=[{"control": "plain_bullets", "verdict": "skill wins"}])),
]


@pytest.mark.parametrize("defn, obj", VALID)
def test_valid_fixtures(defn, obj):
    assert records.validate(obj, defn) == []


@pytest.mark.parametrize("defn, obj", INVALID)
def test_invalid_fixtures(defn, obj):
    assert records.validate(obj, defn) != []


def test_validate_or_raise():
    with pytest.raises(records.SchemaError):
        records.validate_or_raise(_sample(method="nope"), "Sample")
    records.validate_or_raise(_sample(), "Sample")


def test_queue_entry_oneof():
    judge_entry = {"judge": "sol", "sample_id": "a/b/skill", "model": "gpt-5.6-sol", "state": "pending",
                   "attempts": 0, "next_attempt_at": "2026-09-27T00:00:00Z", "first_attempt_at": None}
    assert records.validate(judge_entry, "QueueEntry") == []
    ann = {"annotator": "qwen_annotator", "case_id": "wildchat-01", "model": "qwen/qwen3.8-27b:free",
           "state": "pending", "attempts": 0, "next_attempt_at": "x", "first_attempt_at": None}
    assert records.validate(ann, "QueueEntry") == []
    both = dict(judge_entry, annotator="qwen_annotator", case_id="c")
    assert records.validate(both, "QueueEntry") != []


def test_judge_output_schema():
    good = {"facts": {"f1": {"status": "retained", "evidence": "x"}}, "relations": {}}
    assert records.validate(good, schema="judge-output") == []
    bad_status = {"facts": {"f1": {"status": "lost", "evidence": ""}}, "relations": {}}
    assert records.validate(bad_status, schema="judge-output") != []
    bad_key = {"facts": {"x1": {"status": "retained", "evidence": ""}}, "relations": {}}
    assert records.validate(bad_key, schema="judge-output") != []
    extra_top = {"facts": {}, "relations": {}, "notes": "x"}
    assert records.validate(extra_top, schema="judge-output") != []


def test_json_bytes_equal_canonical(tmp_path):
    obj = {"b": 1, "a": ["é", {"z": None}]}
    p = tmp_path / "x" / "out.json"
    written = records.write_json(p, obj)
    assert written == canonical_json_bytes(obj)
    assert p.read_bytes() == canonical_json_bytes(obj)
    assert records.read_json(p) == obj


def test_jsonl_roundtrip_and_line_format(tmp_path):
    rows = [{"b": 1, "a": "é"}, {"c": [1, 2]}]
    p = tmp_path / "rows.jsonl"
    records.write_jsonl(p, rows)
    raw = p.read_bytes()
    assert raw == b"".join(records.jsonl_line(r) for r in rows)
    assert records.jsonl_line(rows[0]) == '{"a":"é","b":1}\n'.encode("utf-8")
    assert records.read_jsonl(p) == rows
    # Every line is itself valid JSON with sorted keys.
    for line in raw.decode("utf-8").splitlines():
        obj = json.loads(line)
        assert list(obj) == sorted(obj)


def test_atomic_write_leaves_no_temp(tmp_path):
    p = tmp_path / "a.json"
    records.write_json(p, {"x": 1})
    records.write_json(p, {"x": 2})
    assert sorted(q.name for q in tmp_path.iterdir()) == ["a.json"]
    assert records.read_json(p) == {"x": 2}


def test_schema_files_are_local_copies():
    here = Path(records.__file__).resolve().parent.parent / "schemas"
    assert (here / "records.schema.json").is_file()
    assert (here / "judge-output.schema.json").is_file()


def test_schema_copies_match_contracts(paths):
    dc = paths["DC"]
    if not dc.is_dir():
        pytest.skip("DomI contracts checkout not present")
    for name in ("records.schema.json", "judge-output.schema.json"):
        local = Path(records.__file__).resolve().parent.parent / "schemas" / name
        assert local.read_bytes() == (dc / name).read_bytes(), name


def test_module_never_uploads():
    src = Path(records.__file__).read_text(encoding="utf-8").lower()
    for term in ("http", "urllib", "socket"):
        assert term not in src, term
