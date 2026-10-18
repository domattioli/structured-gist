"""The 42 frozen items (tasks T009, FR-003)."""
from __future__ import annotations

import hashlib
import json
import subprocess

import pytest

from bench import items, records


@pytest.fixture(scope="module")
def built():
    return items.build_items()


def _ev_tracked_digest(paths) -> str:
    """SHA-256 over every git-tracked file under EV/ (path + bytes). Ignored
    files such as __pycache__ are excluded because only `git ls-files`
    output is hashed."""
    ev = paths["EV"]
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "."], cwd=ev, capture_output=True, check=True
    ).stdout
    names = sorted(n for n in out.decode("utf-8").split("\0") if n)
    assert names, "no tracked EV files found"
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode("utf-8") + b"\0")
        h.update((ev / n).read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def test_counts(built):
    assert len(built) == 42
    per = {}
    for it in built:
        per[it["dataset"]] = per.get(it["dataset"], 0) + 1
    assert per == {"qmsum": 24, "qasper": 10, "hotpotqa": 8}


def test_item_ids_unique_and_shaped(built):
    ids = [it["item_id"] for it in built]
    assert len(set(ids)) == 42
    for it in built:
        assert it["item_id"] == f"{it['dataset']}/{it['case_id']}"


def test_relation_totals(built):
    assert items.relation_totals(built) == {"qmsum": 50, "qasper": 5, "hotpotqa": 7}


def test_zero_relation_counts(built):
    assert items.zero_relation_case_counts(built) == {"qmsum": 3, "qasper": 6, "hotpotqa": 1}


def test_fact_weights_in_range(built):
    for it in built:
        assert it["facts"], it["item_id"]
        for f in it["facts"]:
            assert 1 <= f["weight"] <= 3, (it["item_id"], f["id"])


def test_source_sha_matches_manifest(built, paths):
    manifest = json.loads((paths["EV"] / "MANIFEST.json").read_text(encoding="utf-8"))
    by_case = {c["case_id"]: c for c in manifest["cases"]}
    for it in built:
        assert it["source_sha256"] == by_case[it["case_id"]]["source_sha256"]


def test_manifest_integrity_passes():
    # Recomputed per-case hashes (source.md + external_gold.json, derived
    # gold, blind weights) equal the committed manifests.
    assert items.manifest_problems() == []


def test_manifest_hash_check_against_prereg(tmp_path):
    shas = items.manifest_sha256s()
    assert items.check_prereg_manifests({"corpus": {
        "corpus_manifest_sha256": shas["corpus_manifest_sha256"],
        "derived_manifest_sha256": shas["derived_manifest_sha256"],
    }}) == []
    bad = items.check_prereg_manifests({"corpus": {
        "corpus_manifest_sha256": "0" * 64,
        "derived_manifest_sha256": shas["derived_manifest_sha256"],
    }})
    assert bad and "corpus_manifest_sha256" in bad[0]


def test_reference_fields_from_external_gold(built, paths):
    it = next(i for i in built if i["case_id"] == "qmsum-01")
    ext = json.loads((paths["EV"] / "qmsum/cases/qmsum-01/external_gold.json").read_text(encoding="utf-8"))
    assert it["reference_answer"] == ext["reference_answer"]
    assert it["question_or_query"] == ext["question_or_query"]


def test_items_validate_against_schema(built):
    for it in built:
        assert records.validate({"item": it}, "ItemLine") == [], it["item_id"]


def test_judge_view_projection(built):
    for it in built:
        view = items.judge_view(it)
        assert set(view) == {"facts", "relations"}
        for f in view["facts"]:
            assert set(f) == {"id", "text", "category"}
        for r in view["relations"]:
            assert set(r) == {"id", "text", "type", "fact_ids"}
        # Only the listed keys survive: no source_quote, weight, question,
        # reference_answer, derived_from, adjudication, or evidence_mode.
        assert [f["id"] for f in view["facts"]] == [f["id"] for f in it["facts"]]
        assert [r["id"] for r in view["relations"]] == [r["id"] for r in it["relations"]]


def test_build_items_writes_jsonl_and_keeps_ev_read_only(tmp_path, paths):
    before = _ev_tracked_digest(paths)
    run_dir = tmp_path / "runs" / "t"
    out = items.write_items(run_dir, items.build_items())
    after = _ev_tracked_digest(paths)
    assert before == after
    assert out == run_dir / "items.jsonl"
    rows = records.read_jsonl(out)
    assert len(rows) == 42
    assert all(set(r) == {"item"} for r in rows)
    # Deterministic bytes on a rebuild.
    first = out.read_bytes()
    items.write_items(run_dir, items.build_items())
    assert out.read_bytes() == first


def test_source_words_use_benchmark_counter(built, paths):
    from bench import words

    it = next(i for i in built if i["case_id"] == "hotpotqa-01")
    src = (paths["EV"] / "hotpotqa/cases/hotpotqa-01/source.md").read_text(encoding="utf-8")
    assert it["source_words"] == words.count_words(src)
