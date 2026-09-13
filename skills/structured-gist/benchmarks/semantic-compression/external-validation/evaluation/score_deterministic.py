#!/usr/bin/env python3
"""
Runs every metric that needs no semantic judge against the frozen external
renderings: compression, structural conformance (reuses ../scoring/
deterministic.py's score_case_tier_level, i.e. the real linter, unmodified),
and wording fidelity (reuses ../scoring/wording_fidelity.py's
score_rendering, unmodified). No model calls. Fully deterministic --
re-running this script against the same renderings reproduces byte-identical
output.

Writes one file per dataset: evaluation/<dataset>/deterministic_scores.json.

Run: python3 score_deterministic.py [--dataset qmsum|qasper|hotpotqa|all]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXTERNAL_VALIDATION = Path(__file__).resolve().parent.parent
SCORING = EXTERNAL_VALIDATION.parent / "scoring"
sys.path.insert(0, str(SCORING))
sys.path.insert(0, str(EXTERNAL_VALIDATION / "scripts"))
import deterministic  # noqa: E402 -- ../scoring/deterministic.py
import wording_fidelity  # noqa: E402 -- ../scoring/wording_fidelity.py
from corpus_lib import canonical_json_bytes  # noqa: E402

LEVELS = ["skim", "standard", "deep"]
DATASETS = ("qmsum", "qasper", "hotpotqa")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def score_dataset(dataset: str) -> dict:
    cases_dir = EXTERNAL_VALIDATION / dataset / "cases"
    renderings_dir = EXTERNAL_VALIDATION / "evaluation" / dataset / "renderings"
    results = {}

    for case_dir in sorted(cases_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        case_id = case_dir.name
        source_path = case_dir / "source.md"
        source_text = source_path.read_text("utf-8")
        source_hash = sha256_hex(source_text)

        rendering_dir = renderings_dir / case_id
        results[case_id] = {}
        for level in LEVELS:
            rendering_path = rendering_dir / f"{level}.md"
            det = deterministic.score_case_tier_level(rendering_path, source_text)
            entry = {"input_sha256": source_hash, **det}
            if rendering_path.exists():
                rendering_text = rendering_path.read_text("utf-8")
                entry["output_sha256"] = sha256_hex(rendering_text)
                entry["wording_fidelity"] = wording_fidelity.score_rendering(rendering_text, source_text)
            else:
                entry["output_sha256"] = None
                entry["wording_fidelity"] = None
            results[case_id][level] = entry

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=[*DATASETS, "all"], default="all")
    args = parser.parse_args()

    targets = list(DATASETS) if args.dataset == "all" else [args.dataset]
    for dataset in targets:
        results = score_dataset(dataset)
        out_path = EXTERNAL_VALIDATION / "evaluation" / dataset / "deterministic_scores.json"
        out_path.write_bytes(canonical_json_bytes(results))
        n_scored = sum(
            1 for levels in results.values() for r in levels.values() if r.get("status") == "scored"
        )
        print(f"[{dataset}] {len(results)} cases, {n_scored} (case,level) renderings scored -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
