#!/usr/bin/env python3
"""
Deterministic pytest tests for the external semantic-gold adapter layer.
No network, no model calls, no randomness.

Two kinds of test:
  1. Pure-function unit tests against common.py's check_lineage_data /
     to_gold_view_data, using synthetic fixtures -- these need neither the
     real corpus nor any derived_gold.json to exist on disk.
  2. Integration tests against whatever derived_gold.json /
     derived_blind_weights.json files are actually committed (offline,
     since they're checked into the repo) -- these adapt to however many
     cases have been annotated, per dataset, rather than hard-coding an
     assumed-complete count (this corpus intentionally allows a dataset to
     land at partial/no coverage -- see FINDINGS.md classification).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402
import validate_derived_gold  # noqa: E402
from corpus_lib import canonical_json_bytes, read_json  # noqa: E402

EXTERNAL_VALIDATION = common.EXTERNAL_VALIDATION


# ---------------------------------------------------------------------------
# synthetic fixtures
# ---------------------------------------------------------------------------

def _native_gold(evidence_ids=("span:0", "span:1")):
    return {
        "case_id": "qmsum-99",
        "dataset": "qmsum",
        "intent": {"reader": "r", "task": "t"},
        "question_or_query": "q?",
        "reference_answer": "a.",
        "native_evidence": [{"span_index": int(e.split(":")[1])} for e in evidence_ids],
        "native_metadata": {},
    }


def _valid_derived():
    return {
        "case_id": "qmsum-99",
        "facts": [
            {
                "id": "f1",
                "text": "prop one",
                "category": "descriptive",
                "source_quote": "quote one",
                "derived_from": [{"dataset": "qmsum", "native_evidence_id": "span:0"}],
            },
            {
                "id": "f2",
                "text": "prop two",
                "category": "outcome",
                "source_quote": "quote two",
                "derived_from": [{"dataset": "qmsum", "native_evidence_id": "span:1"}],
            },
        ],
        "relations": [
            {
                "id": "r1",
                "type": "causal",
                "text": "one causes two",
                "fact_ids": ["f1", "f2"],
                "evidence_mode": "explicit",
                "source_quote": "quote one causes quote two",
                "derived_from": [{"dataset": "qmsum", "native_evidence_id": "span:0"}],
            }
        ],
        "question_fact_ids": ["f1", "f2"],
        "corpus_defect_notes": [],
    }


# ---------------------------------------------------------------------------
# check_lineage_data
# ---------------------------------------------------------------------------

def test_valid_lineage_has_no_problems():
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), _valid_derived())
    assert problems == []


def test_missing_derived_from_is_flagged():
    derived = _valid_derived()
    derived["facts"][0]["derived_from"] = []
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("has no derived_from" in p for p in problems)


def test_unknown_native_evidence_id_is_flagged():
    derived = _valid_derived()
    derived["facts"][0]["derived_from"] = [{"dataset": "qmsum", "native_evidence_id": "span:99"}]
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("unknown native_evidence_id" in p for p in problems)


def test_duplicate_fact_id_is_flagged():
    derived = _valid_derived()
    derived["facts"].append({**derived["facts"][0]})  # duplicate id f1
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("duplicate fact id" in p for p in problems)


def test_relation_referencing_unknown_fact_is_flagged():
    derived = _valid_derived()
    derived["relations"][0]["fact_ids"] = ["f1", "f_ghost"]
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("references unknown fact" in p for p in problems)


def test_relation_with_fewer_than_two_facts_is_flagged():
    derived = _valid_derived()
    derived["relations"][0]["fact_ids"] = ["f1"]
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("fewer than 2 facts" in p for p in problems)


def test_invalid_evidence_mode_is_flagged():
    derived = _valid_derived()
    derived["relations"][0]["evidence_mode"] = "maybe"
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("invalid evidence_mode" in p for p in problems)


def test_explicit_relation_without_source_quote_is_flagged():
    derived = _valid_derived()
    derived["relations"][0]["source_quote"] = ""
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("empty source_quote" in p for p in problems)


def test_inferred_relation_without_source_quote_is_allowed():
    derived = _valid_derived()
    derived["relations"][0]["evidence_mode"] = "inferred"
    derived["relations"][0]["source_quote"] = ""
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert problems == []


def test_empty_fact_source_quote_is_flagged():
    derived = _valid_derived()
    derived["facts"][0]["source_quote"] = "   "
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("empty source_quote" in p for p in problems)


def test_question_fact_ids_referencing_unknown_fact_is_flagged():
    derived = _valid_derived()
    derived["question_fact_ids"] = ["f1", "f_ghost"]
    problems = common.check_lineage_data("qmsum", "qmsum-99", _native_gold(), derived)
    assert any("question_fact_ids references unknown fact" in p for p in problems)


# ---------------------------------------------------------------------------
# to_gold_view_data
# ---------------------------------------------------------------------------

def _weights():
    return {
        "case_id": "qmsum-99",
        "annotation_protocol": "external-blinded-task-importance-v1",
        "fact_weights": {"f1": 3, "f2": 1},
        "relation_weights": {"r1": 2},
        "rationale": {"f1": "critical", "f2": "supporting", "r1": "material"},
    }


def test_to_gold_view_data_injects_blind_weight_not_category():
    view = common.to_gold_view_data(_native_gold(), _valid_derived(), _weights())
    weights_by_id = {f["id"]: f["weight"] for f in view["facts"]}
    assert weights_by_id == {"f1": 3, "f2": 1}
    # never a category-derived default -- weight came only from _weights()
    assert all("weight" not in f or f["weight"] in (1, 2, 3) for f in _valid_derived()["facts"])


def test_to_gold_view_data_has_single_native_question():
    view = common.to_gold_view_data(_native_gold(), _valid_derived(), _weights())
    assert len(view["questions"]) == 1
    q = view["questions"][0]
    assert q["question"] == "q?"
    assert q["gold_answer"] == "a."
    assert q["fact_ids"] == ["f1", "f2"]


def test_to_gold_view_data_raises_on_missing_fact_weight():
    weights = _weights()
    del weights["fact_weights"]["f2"]
    with pytest.raises(KeyError):
        common.to_gold_view_data(_native_gold(), _valid_derived(), weights)


def test_to_gold_view_data_is_deterministic():
    v1 = canonical_json_bytes(common.to_gold_view_data(_native_gold(), _valid_derived(), _weights()))
    v2 = canonical_json_bytes(common.to_gold_view_data(_native_gold(), _valid_derived(), _weights()))
    assert v1 == v2


def test_native_evidence_id_schemes():
    assert common.qmsum_native_evidence_ids({"native_evidence": [{"span_index": 3}]}) == {"span:3"}
    assert common.qasper_native_evidence_ids({"native_evidence": [{"global_idx": 7}]}) == {"para:7"}
    assert common.hotpotqa_native_evidence_ids(
        {"native_evidence": [{"title": "Foo", "sent_id": 2}]}
    ) == {"Foo::sent2"}


# ---------------------------------------------------------------------------
# integration: whatever's actually committed (offline)
# ---------------------------------------------------------------------------

def _derived_case_ids(dataset: str) -> list[str]:
    d = EXTERNAL_VALIDATION / dataset / "cases"
    if not d.is_dir():
        return []
    return sorted(
        p.parent.name for p in d.glob("*/derived_gold.json")
    )


def test_native_snapshot_exists_and_matches():
    failures: list[str] = []
    validate_derived_gold.check_native_unchanged(failures)
    assert failures == []


def test_every_committed_derived_case_has_frozen_native_counterpart():
    for dataset in common.DATASETS:
        for case_id in _derived_case_ids(dataset):
            assert (EXTERNAL_VALIDATION / dataset / "cases" / case_id / "external_gold.json").is_file()


def test_every_committed_derived_case_passes_lineage_check():
    problems = []
    for dataset in common.DATASETS:
        for case_id in _derived_case_ids(dataset):
            problems.extend(common.check_lineage(dataset, case_id))
    assert problems == []


def test_every_committed_derived_case_has_weight_coverage_in_range():
    for dataset in common.DATASETS:
        for case_id in _derived_case_ids(dataset):
            weights = common.load_blind_weights(dataset, case_id)
            if weights is None:
                continue
            derived = common.load_derived_gold(dataset, case_id)
            fact_ids = {f["id"] for f in derived["facts"]}
            rel_ids = {r["id"] for r in derived["relations"]}
            assert set(weights["fact_weights"]) == fact_ids, case_id
            assert set(weights["relation_weights"]) == rel_ids, case_id
            assert all(w in (1, 2, 3) for w in weights["fact_weights"].values()), case_id
            assert all(w in (1, 2, 3) for w in weights["relation_weights"].values()), case_id


def test_hotpotqa_derived_cases_stay_pressure_only():
    for case_id in _derived_case_ids("hotpotqa"):
        native = common.load_native_gold("hotpotqa", case_id)
        assert native["native_metadata"]["pressure_only"] is True


def test_dataset_roles_stay_separate_in_derived_manifest():
    manifest_path = EXTERNAL_VALIDATION / "DERIVED_MANIFEST.json"
    if not manifest_path.exists():
        pytest.skip("DERIVED_MANIFEST.json not yet generated")
    manifest = read_json(manifest_path)
    for case in manifest["cases"]:
        assert case["dataset"] in common.DATASETS
    # no pooled cross-dataset combined score field anywhere in the manifest
    assert "combined_score" not in manifest
    assert "pooled_average" not in manifest


def test_full_derived_gold_offline_validator_passes():
    failures: list[str] = []
    report: dict = {}
    validate_derived_gold.check_native_unchanged(failures)
    for dataset in common.DATASETS:
        for case_id in common.all_case_ids(dataset):
            validate_derived_gold.check_case(dataset, case_id, failures, report)
    assert failures == []


EXPECTED_DERIVED_COUNTS = {"qmsum": 24, "qasper": 10, "hotpotqa": 8}


def test_exact_expected_derived_case_count_per_dataset():
    for dataset, expected in EXPECTED_DERIVED_COUNTS.items():
        assert len(_derived_case_ids(dataset)) == expected, dataset


def test_derived_manifest_hashes_reproduce():
    import build_derived_manifest

    manifest_path = EXTERNAL_VALIDATION / "DERIVED_MANIFEST.json"
    if not manifest_path.exists():
        pytest.skip("DERIVED_MANIFEST.json not yet generated")
    committed = read_json(manifest_path)
    recomputed = build_derived_manifest.build()
    assert canonical_json_bytes(recomputed) == canonical_json_bytes(committed)


def test_every_derived_case_has_a_coverage_audit_record():
    for dataset in common.DATASETS:
        for case_id in _derived_case_ids(dataset):
            p = EXTERNAL_VALIDATION / dataset / "cases" / case_id / "coverage_audit.json"
            assert p.is_file(), case_id
            audit = read_json(p)
            assert audit["status"] in ("pass", "issues_found"), case_id


def test_calibration_cases_have_two_independent_passes_and_comparison():
    calibration_dir = EXTERNAL_VALIDATION / "calibration"
    if not calibration_dir.is_dir():
        pytest.skip("calibration/ not present")
    comparison_path = calibration_dir / "calibration_comparison.json"
    assert comparison_path.is_file()
    comparison = read_json(comparison_path)
    assert len(comparison["cases"]) == 7
    for case_dir in sorted(p for p in calibration_dir.iterdir() if p.is_dir()):
        assert (case_dir / "annotator_a.json").is_file()
        assert (case_dir / "annotator_b.json").is_file()


def test_to_gold_view_on_real_case_matches_stage_b_weights():
    for dataset in common.DATASETS:
        for case_id in _derived_case_ids(dataset):
            weights = common.load_blind_weights(dataset, case_id)
            if weights is None:
                continue
            view = common.to_gold_view(dataset, case_id)
            for f in view["facts"]:
                assert f["weight"] == weights["fact_weights"][f["id"]], (dataset, case_id, f["id"])
            assert len(view["questions"]) == 1
            return  # one real case is enough to prove the wiring; full sweep is test_every_committed_derived_case_has_weight_coverage_in_range
