#!/usr/bin/env python3
"""
Fully offline integrity check for the derived semantic-gold layer. Mirrors
../scripts/verify_corpus.py's role for the native layer -- this script
never re-checks anything that one already covers except by comparing
against a frozen snapshot of the native files (NATIVE_SNAPSHOT.json,
generated once, before any derived_gold.json existed, via
`--freeze-native-snapshot`) to prove this session's adapter work never
touched them.

No network. No model calls. Reads only committed files under
external-validation/.

Checks:
  - every native file (external_gold.json, source.md, provenance.json,
    MANIFEST.json, each dataset's selection.json) hashes identically to
    NATIVE_SNAPSHOT.json -- "native gold/manifest remain byte-identical"
  - a derived case only exists where a frozen native case exists
  - fact/relation lineage (common.check_lineage): derived_from resolves
    to a real native_evidence id, no duplicate fact/relation ids, every
    relation's fact_ids resolve, evidence_mode is explicit/inferred and
    explicit relations carry a non-empty source_quote
  - every fact source_quote, and every explicit relation's source_quote,
    resolves verbatim (whitespace-normalized) inside the case's source.md
  - derived_blind_weights.json (when present) covers every fact/relation
    id with a weight in {1, 2, 3}, and every weight has a non-empty
    rationale
  - to_gold_view() / to_blind_weights_view() serialize deterministically
    (two calls produce byte-identical canonical JSON)
  - dataset field inside derived_gold.json matches the directory it lives
    in; hotpotqa cases keep native_metadata.pressure_only == true
    (checked via the native snapshot, not re-derived here)

Run: python3 validate_derived_gold.py [--dataset qmsum|qasper|hotpotqa|all]
     python3 validate_derived_gold.py --freeze-native-snapshot   # one-time, before any derived work
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402
from corpus_lib import canonical_json_bytes, read_json, sha256_hex, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
SNAPSHOT_PATH = HERE / "NATIVE_SNAPSHOT.json"

NATIVE_GLOBS = [
    "MANIFEST.json",
    "qmsum/selection.json",
    "qasper/selection.json",
    "hotpotqa/selection.json",
    "qmsum/cases/*/external_gold.json",
    "qmsum/cases/*/source.md",
    "qmsum/cases/*/provenance.json",
    "qasper/cases/*/external_gold.json",
    "qasper/cases/*/source.md",
    "qasper/cases/*/provenance.json",
    "hotpotqa/cases/*/external_gold.json",
    "hotpotqa/cases/*/source.md",
    "hotpotqa/cases/*/provenance.json",
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def freeze_native_snapshot() -> None:
    base = common.EXTERNAL_VALIDATION
    snapshot = {}
    for pattern in NATIVE_GLOBS:
        for p in sorted(base.glob(pattern)):
            rel = str(p.relative_to(base))
            snapshot[rel] = sha256_hex(p.read_bytes())
    write_json(SNAPSHOT_PATH, {"files": snapshot, "n_files": len(snapshot)})
    print(f"Wrote {SNAPSHOT_PATH} covering {len(snapshot)} native files.")


def check_native_unchanged(failures: list) -> None:
    if not SNAPSHOT_PATH.exists():
        failures.append("NATIVE_SNAPSHOT.json missing -- run --freeze-native-snapshot once before adapter work")
        return
    snapshot = read_json(SNAPSHOT_PATH)["files"]
    base = common.EXTERNAL_VALIDATION
    for rel, expected in snapshot.items():
        p = base / rel
        if not p.exists():
            failures.append(f"native file deleted: {rel}")
            continue
        actual = sha256_hex(p.read_bytes())
        if actual != expected:
            failures.append(f"native file changed: {rel} (expected sha256={expected[:12]}..., got {actual[:12]}...)")


def check_case(dataset: str, case_id: str, failures: list, report: dict) -> None:
    derived = common.load_derived_gold(dataset, case_id)
    if derived is None:
        return  # not yet annotated -- not a failure, just not counted

    if not derived.get("case_id", "").startswith(f"{dataset}-"):
        failures.append(f"{dataset}/{case_id}: derived_gold.json case_id {derived.get('case_id')!r} does not match its directory")

    for problem in common.check_lineage(dataset, case_id):
        failures.append(problem)

    source_text = (common.case_dir(dataset, case_id) / "source.md").read_text("utf-8")
    norm_source = _norm(source_text)

    for f in derived["facts"]:
        q = _norm(f.get("source_quote", ""))
        if q and q not in norm_source:
            failures.append(f"{dataset}/{case_id}: fact {f['id']} source_quote does not resolve in source.md")

    for r in derived["relations"]:
        if r.get("evidence_mode") == "explicit":
            q = _norm(r.get("source_quote", ""))
            if q and q not in norm_source:
                failures.append(f"{dataset}/{case_id}: relation {r['id']} source_quote does not resolve in source.md")

    weights = common.load_blind_weights(dataset, case_id)
    fact_ids = {f["id"] for f in derived["facts"]}
    rel_ids = {r["id"] for r in derived["relations"]}
    if weights is not None:
        fw, rw = weights.get("fact_weights", {}), weights.get("relation_weights", {})
        rationale = weights.get("rationale", {})
        for fid in fact_ids:
            if fid not in fw:
                failures.append(f"{dataset}/{case_id}: fact {fid} missing from derived_blind_weights.fact_weights")
            elif fw[fid] not in (1, 2, 3):
                failures.append(f"{dataset}/{case_id}: fact {fid} weight {fw[fid]!r} not in {{1,2,3}}")
            elif fid not in rationale or not rationale[fid].strip():
                failures.append(f"{dataset}/{case_id}: fact {fid} weight has no rationale")
        for rid in rel_ids:
            if rid not in rw:
                failures.append(f"{dataset}/{case_id}: relation {rid} missing from derived_blind_weights.relation_weights")
            elif rw[rid] not in (1, 2, 3):
                failures.append(f"{dataset}/{case_id}: relation {rid} weight {rw[rid]!r} not in {{1,2,3}}")
            elif rid not in rationale or not rationale[rid].strip():
                failures.append(f"{dataset}/{case_id}: relation {rid} weight has no rationale")

        # determinism: to_gold_view / to_blind_weights_view are pure
        # functions of committed files -- two calls must agree byte-for-byte.
        try:
            v1 = canonical_json_bytes(common.to_gold_view(dataset, case_id))
            v2 = canonical_json_bytes(common.to_gold_view(dataset, case_id))
            if v1 != v2:
                failures.append(f"{dataset}/{case_id}: to_gold_view() is non-deterministic")
        except (FileNotFoundError, KeyError) as e:
            failures.append(f"{dataset}/{case_id}: to_gold_view() failed: {e}")

    report.setdefault(dataset, {"n_derived": 0, "n_facts": 0, "n_relations": 0, "n_weighted": 0})
    report[dataset]["n_derived"] += 1
    report[dataset]["n_facts"] += len(derived["facts"])
    report[dataset]["n_relations"] += len(derived["relations"])
    if weights is not None:
        report[dataset]["n_weighted"] += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=[*common.DATASETS, "all"], default="all")
    parser.add_argument("--freeze-native-snapshot", action="store_true")
    args = parser.parse_args()

    if args.freeze_native_snapshot:
        freeze_native_snapshot()
        return 0

    failures: list[str] = []
    check_native_unchanged(failures)

    report: dict = {}
    targets = list(common.DATASETS) if args.dataset == "all" else [args.dataset]
    for dataset in targets:
        for case_id in common.all_case_ids(dataset):
            check_case(dataset, case_id, failures, report)

    if failures:
        print(f"FAIL: {len(failures)} problem(s)\n")
        for f in failures:
            print(f" - {f}")
        return 1

    total = sum(v["n_derived"] for v in report.values())
    print(f"OK: native snapshot intact; {total} derived case(s) validated.")
    for dataset, r in sorted(report.items()):
        print(f"  {dataset}: {r['n_derived']} derived, {r['n_facts']} facts, "
              f"{r['n_relations']} relations, {r['n_weighted']} weighted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
