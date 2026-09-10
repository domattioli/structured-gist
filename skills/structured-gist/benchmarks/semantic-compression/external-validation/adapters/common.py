#!/usr/bin/env python3
"""
Shared adapter machinery: loads native + derived gold, validates lineage,
and exposes scorer-compatible views generated at runtime. See
ADAPTER_DESIGN.md for the full architecture and why `to_gold_view()`
builds its dict in memory rather than a committed `gold.json` file.

No network. No model calls. This module never mutates
external_gold.json, source.md, provenance.json, or MANIFEST.json (the
frozen native layer from PR #19) -- it only reads them.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

EXTERNAL_VALIDATION = Path(__file__).resolve().parent.parent
DATASETS = ("qmsum", "qasper", "hotpotqa")

sys.path.insert(0, str(EXTERNAL_VALIDATION / "scripts"))
from corpus_lib import canonical_json_bytes, read_json, sha256_hex, write_json  # noqa: E402


def case_dir(dataset: str, case_id: str) -> Path:
    if dataset not in DATASETS:
        raise ValueError(f"unknown dataset: {dataset!r}")
    return EXTERNAL_VALIDATION / dataset / "cases" / case_id


def all_case_ids(dataset: str) -> list[str]:
    d = EXTERNAL_VALIDATION / dataset / "cases"
    return sorted(p.name for p in d.iterdir() if p.is_dir())


def load_native_gold(dataset: str, case_id: str) -> dict:
    return read_json(case_dir(dataset, case_id) / "external_gold.json")


def load_native_provenance(dataset: str, case_id: str) -> dict:
    return read_json(case_dir(dataset, case_id) / "provenance.json")


def load_derived_gold(dataset: str, case_id: str) -> dict | None:
    p = case_dir(dataset, case_id) / "derived_gold.json"
    return read_json(p) if p.exists() else None


def load_blind_weights(dataset: str, case_id: str) -> dict | None:
    p = case_dir(dataset, case_id) / "derived_blind_weights.json"
    return read_json(p) if p.exists() else None


def write_derived_gold(dataset: str, case_id: str, derived: dict) -> bytes:
    return write_json(case_dir(dataset, case_id) / "derived_gold.json", derived)


def write_blind_weights(dataset: str, case_id: str, weights: dict) -> bytes:
    return write_json(case_dir(dataset, case_id) / "derived_blind_weights.json", weights)


# ---------------------------------------------------------------------------
# native-evidence-id helpers (one per dataset -- see ADAPTER_DESIGN.md
# "Native-evidence-id scheme"). Kept here, not in the per-dataset modules,
# since validate_derived_gold.py needs all three regardless of which
# dataset it's checking.
# ---------------------------------------------------------------------------

def qmsum_native_evidence_ids(native_gold: dict) -> set[str]:
    return {f"span:{e['span_index']}" for e in native_gold["native_evidence"]}


def qasper_native_evidence_ids(native_gold: dict) -> set[str]:
    return {f"para:{e['global_idx']}" for e in native_gold["native_evidence"]}


def hotpotqa_native_evidence_ids(native_gold: dict) -> set[str]:
    return {f"{e['title']}::sent{e['sent_id']}" for e in native_gold["native_evidence"]}


NATIVE_EVIDENCE_ID_FN = {
    "qmsum": qmsum_native_evidence_ids,
    "qasper": qasper_native_evidence_ids,
    "hotpotqa": hotpotqa_native_evidence_ids,
}


def native_evidence_ids(dataset: str, native_gold: dict) -> set[str]:
    return NATIVE_EVIDENCE_ID_FN[dataset](native_gold)


# ---------------------------------------------------------------------------
# runtime scorer-compatible views
# ---------------------------------------------------------------------------

def to_gold_view(dataset: str, case_id: str) -> dict:
    """Builds a gold.json-compatible dict (facts/relations/questions/intent)
    in memory from derived_gold.json + derived_blind_weights.json. Every
    fact's `weight` comes from the Stage-B blind annotation, never a
    category default -- see ADAPTER_DESIGN.md "Weight strategy". Raises if
    either input file is missing or weight coverage is incomplete (same
    "coverage is a precondition, not a runtime fallback" stance
    ../scoring/spr.py takes for its own blind_weights lookups).
    """
    native = load_native_gold(dataset, case_id)
    derived = load_derived_gold(dataset, case_id)
    weights = load_blind_weights(dataset, case_id)
    if derived is None:
        raise FileNotFoundError(f"no derived_gold.json for {dataset}/{case_id}")
    if weights is None:
        raise FileNotFoundError(f"no derived_blind_weights.json for {dataset}/{case_id}")
    return to_gold_view_data(native, derived, weights)


def to_gold_view_data(native: dict, derived: dict, weights: dict) -> dict:
    """Pure version of to_gold_view(): no file I/O, so tests can exercise
    it with synthetic fixtures instead of the real corpus."""
    case_id = derived.get("case_id", "?")
    fw = weights["fact_weights"]
    facts = []
    for f in derived["facts"]:
        if f["id"] not in fw:
            raise KeyError(f"{case_id}: fact {f['id']} has no Stage-B weight")
        facts.append({**f, "weight": fw[f["id"]]})

    rw = weights["relation_weights"]
    for r in derived["relations"]:
        if r["id"] not in rw:
            raise KeyError(f"{case_id}: relation {r['id']} has no Stage-B weight")
    relations = list(derived["relations"])

    question = {
        "id": "q1",
        "question": native["question_or_query"],
        "gold_answer": native["reference_answer"],
        "type": "factual",
        "fact_ids": derived.get("question_fact_ids", []),
    }

    return {
        "case_id": derived["case_id"],
        "intent": native["intent"],
        "facts": facts,
        "relations": relations,
        "questions": [question],
    }


def to_blind_weights_view(dataset: str, case_id: str) -> dict:
    """Already ../scoring/blind_weights/*.json-compatible; returned as-is."""
    weights = load_blind_weights(dataset, case_id)
    if weights is None:
        raise FileNotFoundError(f"no derived_blind_weights.json for {dataset}/{case_id}")
    return weights


def write_gold_view_file(dataset: str, case_id: str, dest: Path) -> bytes:
    """For a future tool that hard-requires a literal gold.json path. Not
    called anywhere in this PR -- see ADAPTER_DESIGN.md."""
    return write_json(dest, to_gold_view(dataset, case_id))


# ---------------------------------------------------------------------------
# lineage validation (used by validate_derived_gold.py)
# ---------------------------------------------------------------------------

def check_lineage(dataset: str, case_id: str) -> list[str]:
    """Returns a list of problems (empty if none). Fully offline. Thin I/O
    wrapper around check_lineage_data (below), which is the pure, directly
    unit-testable version with no filesystem dependency."""
    native = load_native_gold(dataset, case_id)
    derived = load_derived_gold(dataset, case_id)
    if derived is None:
        return [f"{dataset}/{case_id}: missing derived_gold.json"]
    return check_lineage_data(dataset, case_id, native, derived)


def check_lineage_data(dataset: str, case_id: str, native: dict, derived: dict) -> list[str]:
    """Pure function: no file I/O, no dependency on the real corpus being
    on disk. Same checks as check_lineage(), operating on in-memory dicts
    so tests can exercise it with synthetic fixtures."""
    problems = []
    valid_ids = native_evidence_ids(dataset, native)
    fact_ids = set()
    for f in derived["facts"]:
        if f["id"] in fact_ids:
            problems.append(f"{dataset}/{case_id}: duplicate fact id {f['id']}")
        fact_ids.add(f["id"])
        if not f.get("derived_from"):
            problems.append(f"{dataset}/{case_id}: fact {f['id']} has no derived_from")
        for ref in f.get("derived_from", []):
            if ref.get("dataset") != dataset:
                problems.append(f"{dataset}/{case_id}: fact {f['id']} derived_from wrong dataset {ref.get('dataset')!r}")
            if ref.get("native_evidence_id") not in valid_ids:
                problems.append(
                    f"{dataset}/{case_id}: fact {f['id']} derived_from unknown native_evidence_id {ref.get('native_evidence_id')!r}"
                )
        if not (f.get("source_quote") or "").strip():
            problems.append(f"{dataset}/{case_id}: fact {f['id']} has empty source_quote")

    rel_ids = set()
    for r in derived["relations"]:
        if r["id"] in rel_ids:
            problems.append(f"{dataset}/{case_id}: duplicate relation id {r['id']}")
        rel_ids.add(r["id"])
        if len(r.get("fact_ids", [])) < 2:
            problems.append(f"{dataset}/{case_id}: relation {r['id']} references fewer than 2 facts")
        for fid in r.get("fact_ids", []):
            if fid not in fact_ids:
                problems.append(f"{dataset}/{case_id}: relation {r['id']} references unknown fact {fid!r}")
        mode = r.get("evidence_mode")
        if mode not in ("explicit", "inferred"):
            problems.append(f"{dataset}/{case_id}: relation {r['id']} has invalid evidence_mode {mode!r}")
        if mode == "explicit" and not (r.get("source_quote") or "").strip():
            problems.append(f"{dataset}/{case_id}: relation {r['id']} is explicit but has empty source_quote")
        for ref in r.get("derived_from", []):
            if ref.get("native_evidence_id") not in valid_ids:
                problems.append(
                    f"{dataset}/{case_id}: relation {r['id']} derived_from unknown native_evidence_id {ref.get('native_evidence_id')!r}"
                )

    for qfid in derived.get("question_fact_ids", []):
        if qfid not in fact_ids:
            problems.append(f"{dataset}/{case_id}: question_fact_ids references unknown fact {qfid!r}")

    return problems
