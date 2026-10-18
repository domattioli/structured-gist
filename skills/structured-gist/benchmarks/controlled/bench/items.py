#!/usr/bin/env python3
"""
The 42 frozen benchmark items (FR-003, FR-016).

Items are built from the read-only external-validation tree (EV) through
``adapters/common.py::to_gold_view``, which attaches the Stage-B blind
weights and raises when a weight is missing. ``reference_answer`` and
``question_or_query`` are read from ``EV/<ds>/cases/<id>/external_gold.json``;
they are used only by the secondary graders and never reach a generator or a
judge.

Hash checks (nothing in EV is ever written):
- ``MANIFEST.json``: per case, ``transformed_case_sha256`` must equal
  sha256(source.md bytes + external_gold.json bytes), recomputed from the
  committed files. ``source_sha256`` in the manifest is the hash of the
  *upstream* payload (verify_corpus.py docstring); it cannot be recomputed
  offline and is copied into each item unchanged.
- ``DERIVED_MANIFEST.json``: per case, ``derived_gold_sha256`` and
  ``blind_weights_sha256`` must equal the committed files' hashes.
- The SHA-256 of both manifest files is pinned in ``prereg.json``
  (``corpus.corpus_manifest_sha256``, ``corpus.derived_manifest_sha256``).

No network. No model calls.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CB = Path(__file__).resolve().parent.parent
EV = CB.parent / "semantic-compression" / "external-validation"
for _p in (EV / "scripts", EV / "adapters"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
_dwb = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # never create __pycache__ inside the frozen EV tree
try:
    import common  # noqa: E402 -- EV/adapters/common.py
finally:
    sys.dont_write_bytecode = _dwb

from bench import records, words  # noqa: E402

DATASETS = ("qmsum", "qasper", "hotpotqa")
EXPECTED_COUNTS = {"qmsum": 24, "qasper": 10, "hotpotqa": 8}


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _load(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def manifest_sha256s(ev: Path = EV) -> dict:
    return {
        "corpus_manifest_sha256": _sha256_file(ev / "MANIFEST.json"),
        "derived_manifest_sha256": _sha256_file(ev / "DERIVED_MANIFEST.json"),
    }


def manifest_problems(ev: Path = EV) -> list[str]:
    """Recomputes every per-case hash the two manifests record and returns
    the mismatches (empty when the frozen tree is intact)."""
    problems: list[str] = []
    corpus = _load(ev / "MANIFEST.json")
    derived = _load(ev / "DERIVED_MANIFEST.json")
    counts: dict[str, int] = {}
    for c in corpus["cases"]:
        ds, cid = c["dataset"], c["case_id"]
        counts[ds] = counts.get(ds, 0) + 1
        d = ev / ds / "cases" / cid
        got = hashlib.sha256((d / "source.md").read_bytes() + (d / "external_gold.json").read_bytes()).hexdigest()
        if got != c["transformed_case_sha256"]:
            problems.append(f"{ds}/{cid}: transformed_case_sha256 mismatch")
    if counts != EXPECTED_COUNTS:
        problems.append(f"MANIFEST.json case counts {counts} != {EXPECTED_COUNTS}")
    dcases = {c["case_id"]: c for c in derived["cases"]}
    for c in corpus["cases"]:
        ds, cid = c["dataset"], c["case_id"]
        dc = dcases.get(cid)
        if dc is None:
            problems.append(f"{ds}/{cid}: missing from DERIVED_MANIFEST.json")
            continue
        d = ev / ds / "cases" / cid
        if _sha256_file(d / "derived_gold.json") != dc["derived_gold_sha256"]:
            problems.append(f"{ds}/{cid}: derived_gold_sha256 mismatch")
        if _sha256_file(d / "derived_blind_weights.json") != dc["blind_weights_sha256"]:
            problems.append(f"{ds}/{cid}: blind_weights_sha256 mismatch")
    return problems


def check_prereg_manifests(prereg: dict, ev: Path = EV) -> list[str]:
    """Compares the two manifest-file hashes with the pre-registered ones."""
    live = manifest_sha256s(ev)
    corpus = prereg.get("corpus", {})
    return [
        f"corpus.{k}: pre-registered {corpus.get(k)!r} != live {v}"
        for k, v in live.items()
        if corpus.get(k) != v
    ]


def build_item(dataset: str, case_id: str, manifest_case: dict) -> dict:
    gold = common.to_gold_view(dataset, case_id)
    native = common.load_native_gold(dataset, case_id)
    source = (common.case_dir(dataset, case_id) / "source.md").read_text(encoding="utf-8")
    return {
        "item_id": f"{dataset}/{case_id}",
        "dataset": dataset,
        "case_id": case_id,
        "source_sha256": manifest_case["source_sha256"],
        "source_words": words.count_words(source),
        "facts": [
            {"id": f["id"], "text": f["text"], "category": f["category"], "weight": f["weight"]}
            for f in gold["facts"]
        ],
        "relations": [
            {"id": r["id"], "text": r["text"], "type": r["type"], "fact_ids": list(r["fact_ids"])}
            for r in gold["relations"]
        ],
        "reference_answer": native["reference_answer"],
        "question_or_query": native["question_or_query"],
    }


def build_items(ev: Path = EV) -> list[dict]:
    """All 42 items, ordered by dataset (qmsum, qasper, hotpotqa) then case id."""
    corpus = _load(ev / "MANIFEST.json")
    by_case = {c["case_id"]: c for c in corpus["cases"]}
    out = []
    for ds in DATASETS:
        for cid in common.all_case_ids(ds):
            out.append(build_item(ds, cid, by_case[cid]))
    return out


def source_text(item: dict) -> str:
    """The case's source.md, read from EV (never modified)."""
    return (common.case_dir(item["dataset"], item["case_id"]) / "source.md").read_text(encoding="utf-8")


def gold_view(item: dict) -> dict:
    """The scorer-compatible gold view for ``combine.score_semantic``."""
    return common.to_gold_view(item["dataset"], item["case_id"])


def relation_totals(items: list[dict]) -> dict[str, int]:
    out = {ds: 0 for ds in sorted({i["dataset"] for i in items})}
    for it in items:
        out[it["dataset"]] += len(it["relations"])
    return out


def zero_relation_case_counts(items: list[dict]) -> dict[str, int]:
    out = {ds: 0 for ds in sorted({i["dataset"] for i in items})}
    for it in items:
        if not it["relations"]:
            out[it["dataset"]] += 1
    return out


def judge_view(item: dict) -> dict:
    """The only part of an item a judge sees: fact id, text, category and
    relation id, text, type, fact_ids. No source_quote, weight, question, or
    reference answer (contracts/judge-prompt.md)."""
    return {
        "facts": [{"id": f["id"], "text": f["text"], "category": f["category"]} for f in item["facts"]],
        "relations": [
            {"id": r["id"], "text": r["text"], "type": r["type"], "fact_ids": list(r["fact_ids"])}
            for r in item["relations"]
        ],
    }


def write_items(run_dir: Path, items: list[dict]) -> Path:
    """Validates every item and writes ``<run_dir>/items.jsonl`` atomically."""
    rows = []
    for it in items:
        row = {"item": it}
        records.validate_or_raise(row, "ItemLine")
        rows.append(row)
    out = Path(run_dir) / "items.jsonl"
    records.write_jsonl(out, rows)
    return out
