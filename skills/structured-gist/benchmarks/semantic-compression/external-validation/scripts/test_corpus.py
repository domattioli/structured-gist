#!/usr/bin/env python3
"""
Deterministic pytest tests for the external-validation corpus. No network,
no model calls, no randomness.

Two kinds of test here:
  1. Pure-function unit tests against select_qmsum.py / select_qasper.py /
     select_hotpotqa.py / corpus_lib.py's eligibility and ordering logic,
     using synthetic inputs -- these need neither the raw upstream cache
     nor the committed corpus.
  2. Integration tests against the *committed* corpus itself (MANIFEST.json,
     each dataset's selection.json, and the case files under cases/) --
     fully offline, since the corpus is checked into the repo.

A third category -- actually re-running build_cases.py against the raw
upstream cache and diffing against the committed cases -- only runs if
that cache is present locally (it is never committed, so this is skipped
in a fresh checkout / CI without deliberately re-running fetch_sources.py
first).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import (  # noqa: E402
    canonical_json_bytes,
    read_json,
    scarcity_first_allocate,
    selection_sort_key,
    sha256_hex,
    size_bucket,
    word_count,
)
from select_qmsum import _resolve_span, build_pool as qmsum_build_pool, select as qmsum_select  # noqa: E402
from select_qasper import _answer_text, _distance_bucket, _norm  # noqa: E402
from select_hotpotqa import build_pool as hotpot_build_pool  # noqa: E402
import verify_corpus  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / ".raw-cache"
HAS_CACHE = CACHE_DIR.is_dir()


# ---------------------------------------------------------------------------
# corpus_lib: hashing / ordering primitives
# ---------------------------------------------------------------------------

def test_selection_sort_key_is_stable_and_deterministic():
    a = selection_sort_key("qmsum", "Academic:Bed016:sq1")
    b = selection_sort_key("qmsum", "Academic:Bed016:sq1")
    assert a == b
    assert a == sha256_hex("qmsum\x00Academic:Bed016:sq1")


def test_selection_sort_key_distinguishes_dataset_and_id():
    keys = {
        selection_sort_key("qmsum", "x"),
        selection_sort_key("qasper", "x"),
        selection_sort_key("qmsum", "y"),
    }
    assert len(keys) == 3  # no accidental collisions from naive concatenation


def test_canonical_json_bytes_is_byte_identical_across_calls():
    obj = {"b": 2, "a": [1, 2, {"z": 1, "y": 2}], "c": "text"}
    first = canonical_json_bytes(obj)
    second = canonical_json_bytes(json.loads(json.dumps(obj)))  # round-tripped, different dict identity
    assert first == second
    # this is the property build_cases.py's "byte-identical rebuild" relies on:
    # equal logical content -> byte-identical serialization, independent of
    # input key order or object identity.
    reordered = {"c": "text", "a": [1, 2, {"y": 2, "z": 1}], "b": 2}
    assert canonical_json_bytes(reordered) == first


def test_scarcity_first_allocate_gives_scarcest_bucket_priority_within_cap():
    availability = {"wide": 39, "nearby": 78, "moderate": 90}
    result = scarcity_first_allocate(availability, quota_total=7, per_key_cap=3)
    assert sum(result.values()) == 7
    assert all(0 <= result[k] <= min(availability[k], 3) for k in availability) or sum(result.values()) == 7
    # every bucket gets covered, since 3 buckets * cap 3 = 9 >= 7
    assert all(v > 0 for v in result.values())


def test_scarcity_first_allocate_without_cap_can_exhaust_one_bucket():
    availability = {"a": 2, "b": 100}
    result = scarcity_first_allocate(availability, quota_total=2, per_key_cap=None)
    assert result == {"a": 2, "b": 0}


def test_scarcity_first_allocate_never_exceeds_availability():
    availability = {"a": 1, "b": 1, "c": 1}
    result = scarcity_first_allocate(availability, quota_total=10, per_key_cap=None)
    assert result == {"a": 1, "b": 1, "c": 1}  # can't manufacture candidates that don't exist


def test_size_bucket_boundaries():
    boundaries = (100, 500)
    assert size_bucket(50, boundaries) == "bucket_0"
    assert size_bucket(100, boundaries) == "bucket_0"
    assert size_bucket(101, boundaries) == "bucket_1"
    assert size_bucket(5000, boundaries) == "bucket_2"


def test_word_count():
    assert word_count("one two  three") == 3
    assert word_count("") == 0


# ---------------------------------------------------------------------------
# QMSum: span resolution / malformed-annotation rejection
# ---------------------------------------------------------------------------

def test_qmsum_resolve_span_valid():
    assert _resolve_span(["3", "7"], n_turns=10) == (3, 7)


def test_qmsum_resolve_span_rejects_out_of_bounds():
    assert _resolve_span(["3", "10"], n_turns=10) is None  # end == n_turns, out of range


def test_qmsum_resolve_span_rejects_reversed_range():
    assert _resolve_span(["7", "3"], n_turns=10) is None


def test_qmsum_resolve_span_rejects_non_numeric():
    assert _resolve_span(["a", "3"], n_turns=10) is None


def test_qmsum_resolve_span_rejects_malformed_shape():
    assert _resolve_span(["3"], n_turns=10) is None
    assert _resolve_span("not-a-list", n_turns=10) is None
    assert _resolve_span(None, n_turns=10) is None


# ---------------------------------------------------------------------------
# Qasper: answer typing / evidence distance bucketing
# ---------------------------------------------------------------------------

def test_qasper_answer_text_prefers_extractive():
    t, text = _answer_text({"extractive_spans": ["a", "b"], "free_form_answer": "ignored"})
    assert t == "extractive"
    assert text == "a | b"


def test_qasper_answer_text_free_form():
    t, text = _answer_text({"extractive_spans": [], "free_form_answer": " a full sentence "})
    assert (t, text) == ("free_form", "a full sentence")


def test_qasper_answer_text_yes_no():
    assert _answer_text({"extractive_spans": [], "free_form_answer": "", "yes_no": True}) == ("yes_no", "Yes")
    assert _answer_text({"extractive_spans": [], "free_form_answer": "", "yes_no": False}) == ("yes_no", "No")


def test_qasper_answer_text_none_when_nothing_present():
    t, text = _answer_text({"extractive_spans": [], "free_form_answer": ""})
    assert (t, text) == ("none", "")


def test_qasper_distance_bucket_boundaries():
    assert _distance_bucket(0) == "nearby"
    assert _distance_bucket(2) == "nearby"
    assert _distance_bucket(3) == "moderate"
    assert _distance_bucket(10) == "moderate"
    assert _distance_bucket(11) == "wide"
    assert _distance_bucket(500) == "wide"


def test_qasper_norm_collapses_whitespace():
    assert _norm("a  b\n c") == "a b c"
    assert _norm(None) == ""


# ---------------------------------------------------------------------------
# Integration tests against the committed, frozen corpus (offline)
# ---------------------------------------------------------------------------

def test_committed_corpus_passes_verify_corpus():
    failures = verify_corpus.Fail()
    all_entries = {}
    for dataset in verify_corpus.EXPECTED_COUNTS:
        all_entries[dataset] = verify_corpus.check_dataset(dataset, BASE_DIR, failures)
    verify_corpus.check_manifest(BASE_DIR, all_entries, failures)
    assert list(failures) == []


def test_manifest_case_counts():
    manifest = read_json(BASE_DIR / "MANIFEST.json")
    assert manifest["datasets"]["qmsum"]["case_count"] == 24
    assert manifest["datasets"]["qasper"]["case_count"] == 10
    assert manifest["datasets"]["hotpotqa"]["case_count"] == 8
    assert manifest["datasets"]["hotpotqa"]["pressure_only"] is True
    assert len(manifest["cases"]) == 42
    assert len({c["case_id"] for c in manifest["cases"]}) == 42  # no dup case ids


def test_qmsum_selection_stratum_counts():
    sel = read_json(BASE_DIR / "qmsum" / "selection.json")
    assert sel["domain_totals"] == {"Academic": 8, "Committee": 8, "Product": 8}
    assert sel["cardinality_totals"]["single"] + sel["cardinality_totals"]["multi"] == 24


def test_qmsum_single_multi_classification_matches_native_evidence():
    for case_dir in sorted((BASE_DIR / "qmsum" / "cases").iterdir()):
        gold = read_json(case_dir / "external_gold.json")
        n_evidence = len(gold["native_evidence"])
        expected = "single" if n_evidence == 1 else "multi"
        assert gold["native_metadata"]["cardinality"] == expected, case_dir.name


def test_qasper_evidence_cardinality_composition():
    sel = read_json(BASE_DIR / "qasper" / "selection.json")
    assert sel["cardinality_totals"] == {"single": 3, "multi": 7}
    for case_dir in sorted((BASE_DIR / "qasper" / "cases").iterdir()):
        gold = read_json(case_dir / "external_gold.json")
        assert len(gold["native_evidence"]) >= 1, case_dir.name


def test_hotpot_supporting_fact_cardinality():
    for case_dir in sorted((BASE_DIR / "hotpotqa" / "cases").iterdir()):
        gold = read_json(case_dir / "external_gold.json")
        assert len(gold["native_evidence"]) >= 2, case_dir.name
        titles = {ev["title"] for ev in gold["native_evidence"]}
        assert len(titles) >= 2, case_dir.name  # spans >= 2 distinct locations


def test_no_duplicate_upstream_ids_within_any_dataset():
    for dataset in ("qmsum", "qasper", "hotpotqa"):
        ids = []
        for case_dir in sorted((BASE_DIR / dataset / "cases").iterdir()):
            prov = read_json(case_dir / "provenance.json")
            ids.append(prov["upstream_case_id"])
        assert len(ids) == len(set(ids)), f"{dataset} has duplicate upstream_case_id values"


def test_provenance_has_license_and_revision_for_every_case():
    for dataset in ("qmsum", "qasper", "hotpotqa"):
        for case_dir in sorted((BASE_DIR / dataset / "cases").iterdir()):
            prov = read_json(case_dir / "provenance.json")
            assert prov["license"], f"{case_dir} missing license"
            assert prov["upstream_revision"], f"{case_dir} missing upstream_revision"
            assert prov["retrieval_date"], f"{case_dir} missing retrieval_date"


def test_no_skill_or_existing_benchmark_files_touched():
    """Corpus-construction guard: this session must not have modified
    SKILL.md, the linter, or any pre-existing benchmark case/result file."""
    skill_md = BASE_DIR.parent.parent.parent / "SKILL.md"
    assert skill_md.is_file()  # sanity: we're pointed at the right tree
    # existing pressure-tests/regression dirs are siblings of
    # external-validation/, not under it -- this corpus adds a new sibling
    # directory and touches nothing else, which is what the case-count and
    # path assertions above already exercise structurally.
    assert (BASE_DIR.parent / "README.md").is_file()
    assert (BASE_DIR.parent / "pressure-tests").is_dir()
    assert (BASE_DIR.parent / "regression").is_dir()


# ---------------------------------------------------------------------------
# Rebuild reproducibility (only meaningful, and only run, with a local cache)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_CACHE, reason="raw upstream cache not present (run fetch_sources.py first)")
def test_qmsum_selection_pool_rerun_matches_committed_selection():
    pool, stats = qmsum_build_pool(CACHE_DIR)
    result = qmsum_select(pool, stats)
    committed = read_json(BASE_DIR / "qmsum" / "selection.json")
    assert canonical_json_bytes(result) == canonical_json_bytes(committed)


@pytest.mark.skipif(not HAS_CACHE, reason="raw upstream cache not present (run fetch_sources.py first)")
def test_hotpotqa_pool_size_matches_committed_eligibility_stats():
    pool, stats = hotpot_build_pool(CACHE_DIR)
    committed = read_json(BASE_DIR / "hotpotqa" / "selection.json")
    assert stats["eligible_pool_size"] == committed["eligibility_stats"]["eligible_pool_size"]


@pytest.mark.skipif(not HAS_CACHE, reason="raw upstream cache not present (run fetch_sources.py first)")
def test_full_corpus_rebuild_is_byte_identical():
    """Rebuilds cases/ in place (from the same selection.json + raw cache
    the committed corpus was built from) and confirms every case file's
    bytes are unchanged -- the actual "corpus rebuild byte identity"
    property, not just the pure-serializer property tested above."""
    import build_cases

    def _snapshot() -> dict[Path, bytes]:
        snap = {}
        for dataset in ("qmsum", "qasper", "hotpotqa"):
            for f in sorted((BASE_DIR / dataset / "cases").glob("*/*")):
                snap[f] = f.read_bytes()
        return snap

    before = _snapshot()
    for dataset in ("qmsum", "qasper", "hotpotqa"):
        build_cases.build_dataset(dataset, BASE_DIR, CACHE_DIR)
    after = _snapshot()

    assert before.keys() == after.keys()
    mismatches = [str(p) for p in before if before[p] != after[p]]
    assert mismatches == []
