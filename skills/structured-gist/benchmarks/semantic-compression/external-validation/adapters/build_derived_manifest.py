#!/usr/bin/env python3
"""
Builds DERIVED_MANIFEST.json from whatever derived_gold.json /
derived_blind_weights.json / coverage_audit.json files are currently
committed. Safe to run at any point -- with zero derived cases it emits an
empty manifest; it never requires full 24/10/8 coverage (a dataset may
legitimately land at partial or zero derived coverage, see FINDINGS.md).

No network. No model calls. Reads only committed files.

Run: python3 build_derived_manifest.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402
from corpus_lib import read_json, sha256_hex, write_json  # noqa: E402

ADAPTER_VERSION = "1.0.0"
STAGE_A_PROTOCOL_VERSION = "external-semantic-decomposition-v1"


def build() -> dict:
    cases = []
    for dataset in common.DATASETS:
        cases_dir = common.EXTERNAL_VALIDATION / dataset / "cases"
        if not cases_dir.is_dir():
            continue
        for case_path in sorted(cases_dir.iterdir()):
            if not case_path.is_dir():
                continue
            case_id = case_path.name
            derived_path = case_path / "derived_gold.json"
            if not derived_path.exists():
                continue  # not yet annotated -- not an error, just not in the manifest

            derived = read_json(derived_path)
            native_gold_path = case_path / "external_gold.json"
            weights_path = case_path / "derived_blind_weights.json"
            coverage_path = case_path / "coverage_audit.json"

            weights = read_json(weights_path) if weights_path.exists() else None
            coverage = read_json(coverage_path) if coverage_path.exists() else None

            fact_ids_w3 = set()
            rel_ids_w3 = set()
            if weights is not None:
                fact_ids_w3 = {fid for fid, w in weights["fact_weights"].items() if w == 3}
                rel_ids_w3 = {rid for rid, w in weights["relation_weights"].items() if w == 3}

            cases.append(
                {
                    "case_id": case_id,
                    "dataset": dataset,
                    "native_gold_sha256": sha256_hex(native_gold_path.read_bytes()),
                    "derived_gold_sha256": sha256_hex(derived_path.read_bytes()),
                    "blind_weights_sha256": sha256_hex(weights_path.read_bytes()) if weights_path.exists() else None,
                    "adapter_version": ADAPTER_VERSION,
                    "stage_a_protocol_version": STAGE_A_PROTOCOL_VERSION,
                    "stage_b_protocol_version": (weights or {}).get("annotation_protocol"),
                    "annotator_metadata": {
                        "stage_a": derived.get("annotator_metadata", "isolated_llm_agent"),
                        "stage_b": (weights or {}).get("annotator_metadata", "isolated_llm_agent") if weights else None,
                    },
                    "build_date": derived.get("build_date"),
                    "has_relations": len(derived.get("relations", [])) > 0,
                    "fact_count": len(derived.get("facts", [])),
                    "relation_count": len(derived.get("relations", [])),
                    "critical_unit_count": len(fact_ids_w3) + len(rel_ids_w3),
                    "weighted": weights is not None,
                    "coverage_audit_status": (coverage or {}).get("status", "not_run"),
                    "adjudication_status": derived.get("adjudication_status", "single_pass"),
                }
            )

    cases.sort(key=lambda c: (c["dataset"], c["case_id"]))
    manifest = {
        "derived_corpus_version": 1,
        "adapter_version": ADAPTER_VERSION,
        "datasets": {
            d: {"case_count": sum(1 for c in cases if c["dataset"] == d)} for d in common.DATASETS
        },
        "cases": cases,
    }
    return manifest


def main() -> int:
    manifest = build()
    write_json(common.EXTERNAL_VALIDATION / "DERIVED_MANIFEST.json", manifest)
    total = len(manifest["cases"])
    print(f"DERIVED_MANIFEST.json written with {total} derived case(s).")
    for d, info in manifest["datasets"].items():
        print(f"  {d}: {info['case_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
