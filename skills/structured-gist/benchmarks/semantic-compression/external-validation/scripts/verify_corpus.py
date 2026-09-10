#!/usr/bin/env python3
"""
Fully offline integrity check for the frozen external-validation corpus.
No network. No model calls. Reads only committed files under
external-validation/ (MANIFEST.json plus each dataset's cases/).

Checks (see external-validation/README.md "Corpus integrity checks" for
the source-of-truth list this implements):
  - expected per-dataset case counts (24 / 10 / 8)
  - no duplicate upstream IDs within a dataset
  - every case dir has source.md, external_gold.json, provenance.json
  - source.md is non-empty; reference_answer is non-empty
  - every provenance.json field required by the schema is present
  - license/attribution metadata present for every case
  - recomputed transformed_case_sha256 (hash of the committed source.md +
    external_gold.json bytes) matches provenance.json's recorded value.
    source_sha256 (hash of the *upstream* payload before transformation)
    is recorded but not re-verified here -- that would require the raw
    upstream cache, which is not committed; see select_*.py/build_cases.py
    re-run instructions in HANDOFF.md for that check.
  - MANIFEST.json's recorded hashes match a freshly recomputed manifest
    (catches "generated manifest differs from committed manifest" and, by
    construction, "case hashes changed unexpectedly")
  - QMSum: every case's native_evidence is non-empty (has a relevant span);
    single/multi cardinality label matches native_evidence length
  - Qasper: every case has at least one resolved evidence location
  - HotpotQA: every case has >= 2 supporting facts, pressure_only is true

Does NOT check "selection rerun chooses different cases" -- that requires
re-fetching upstream data over the network and is deliberately kept out of
this offline path; see select_*.py --cache-dir to rerun it by hand.

Run: python3 verify_corpus.py --base-dir <path to external-validation/>
Exits non-zero (and prints every failure) if anything is wrong.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import canonical_json_bytes, read_json, sha256_hex  # noqa: E402

EXPECTED_COUNTS = {"qmsum": 24, "qasper": 10, "hotpotqa": 8}
REQUIRED_PROVENANCE_FIELDS = [
    "dataset",
    "upstream_case_id",
    "upstream_document_id",
    "upstream_question_id",
    "upstream_split",
    "upstream_source_repository",
    "upstream_revision",
    "license",
    "license_source",
    "retrieval_date",
    "source_sha256",
    "transformed_case_sha256",
    "transformation_script_version",
    "deviations",
]


class Fail(list):
    def add(self, msg: str) -> None:
        self.append(msg)


def check_dataset(dataset: str, base_dir: Path, failures: Fail) -> list[dict]:
    cases_dir = base_dir / dataset / "cases"
    if not cases_dir.is_dir():
        failures.add(f"[{dataset}] cases/ directory missing")
        return []

    case_dirs = sorted(p for p in cases_dir.iterdir() if p.is_dir())
    if len(case_dirs) != EXPECTED_COUNTS[dataset]:
        failures.add(
            f"[{dataset}] expected {EXPECTED_COUNTS[dataset]} cases, found {len(case_dirs)}"
        )

    seen_upstream_ids = set()
    entries = []

    for case_dir in case_dirs:
        case_id = case_dir.name
        source_path = case_dir / "source.md"
        gold_path = case_dir / "external_gold.json"
        prov_path = case_dir / "provenance.json"

        missing = [p.name for p in (source_path, gold_path, prov_path) if not p.exists()]
        if missing:
            failures.add(f"[{dataset}/{case_id}] missing files: {missing}")
            continue

        source_bytes = source_path.read_bytes()
        if not source_bytes.strip():
            failures.add(f"[{dataset}/{case_id}] source.md is empty")

        gold = read_json(gold_path)
        prov = read_json(prov_path)

        if not (gold.get("reference_answer") or "").strip():
            failures.add(f"[{dataset}/{case_id}] reference_answer is missing/empty")

        missing_fields = [f for f in REQUIRED_PROVENANCE_FIELDS if f not in prov]
        if missing_fields:
            failures.add(f"[{dataset}/{case_id}] provenance.json missing fields: {missing_fields}")
        if not (prov.get("license") or "").strip():
            failures.add(f"[{dataset}/{case_id}] provenance.json has no license recorded")

        upstream_id = prov.get("upstream_case_id")
        if upstream_id in seen_upstream_ids:
            failures.add(f"[{dataset}/{case_id}] duplicate upstream_case_id: {upstream_id}")
        seen_upstream_ids.add(upstream_id)

        gold_bytes = gold_path.read_bytes()
        recomputed_transformed = sha256_hex(source_bytes + gold_bytes)
        if recomputed_transformed != prov.get("transformed_case_sha256"):
            failures.add(
                f"[{dataset}/{case_id}] transformed_case_sha256 mismatch: "
                f"recorded={prov.get('transformed_case_sha256')} recomputed={recomputed_transformed}"
            )

        native_evidence = gold.get("native_evidence")
        native_metadata = gold.get("native_metadata", {})

        if dataset == "qmsum":
            if not native_evidence:
                failures.add(f"[{dataset}/{case_id}] QMSum case has no relevant span (native_evidence empty)")
            expected_cardinality = "single" if len(native_evidence or []) == 1 else "multi"
            if native_metadata.get("cardinality") != expected_cardinality:
                failures.add(
                    f"[{dataset}/{case_id}] cardinality label {native_metadata.get('cardinality')!r} "
                    f"does not match native_evidence length ({len(native_evidence or [])})"
                )
        elif dataset == "qasper":
            if not native_evidence:
                failures.add(f"[{dataset}/{case_id}] Qasper case has no resolved evidence location")
        elif dataset == "hotpotqa":
            if len(native_evidence or []) < 2:
                failures.add(f"[{dataset}/{case_id}] Hotpot case has fewer than 2 supporting facts")
            if native_metadata.get("pressure_only") is not True:
                failures.add(f"[{dataset}/{case_id}] Hotpot case missing pressure_only: true")

        entries.append(
            {
                "case_id": case_id,
                "dataset": dataset,
                "upstream_id": upstream_id,
                "split_or_domain": prov.get("upstream_domain", prov.get("upstream_split")),
                "evidence_cardinality": native_metadata.get("cardinality", "n/a"),
                "source_word_count": native_metadata.get("source_word_count"),
                "source_sha256": prov.get("source_sha256"),
                "transformed_case_sha256": prov.get("transformed_case_sha256"),
                "provenance_path": f"{dataset}/cases/{case_id}/provenance.json",
            }
        )

    entries.sort(key=lambda e: e["case_id"])
    return entries


def check_manifest(base_dir: Path, all_entries: dict[str, list[dict]], failures: Fail) -> None:
    manifest_path = base_dir / "MANIFEST.json"
    if not manifest_path.exists():
        failures.add("MANIFEST.json is missing")
        return
    committed = read_json(manifest_path)

    cases = []
    for entries in all_entries.values():
        cases.extend(entries)
    cases.sort(key=lambda e: e["case_id"])

    from corpus_lib import BUILD_SCRIPT_VERSION

    recomputed = {
        "corpus_version": 1,
        "build_script_version": BUILD_SCRIPT_VERSION,
        "datasets": {
            "qmsum": {"case_count": len(all_entries.get("qmsum", []))},
            "qasper": {"case_count": len(all_entries.get("qasper", []))},
            "hotpotqa": {"case_count": len(all_entries.get("hotpotqa", [])), "pressure_only": True},
        },
        "cases": cases,
    }

    if canonical_json_bytes(recomputed) != canonical_json_bytes(committed):
        failures.add(
            "MANIFEST.json differs from a freshly recomputed manifest over the committed "
            "case files -- either a case was hand-edited after build_cases.py ran, or "
            "MANIFEST.json is stale. Re-run build_cases.py and diff."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    failures = Fail()
    all_entries = {}
    for dataset in EXPECTED_COUNTS:
        all_entries[dataset] = check_dataset(dataset, args.base_dir, failures)

    check_manifest(args.base_dir, all_entries, failures)

    if failures:
        print(f"FAIL: {len(failures)} problem(s) found\n")
        for f in failures:
            print(f" - {f}")
        return 1

    total = sum(len(v) for v in all_entries.values())
    print(f"OK: {total} cases verified across {len(EXPECTED_COUNTS)} datasets, MANIFEST.json matches.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
