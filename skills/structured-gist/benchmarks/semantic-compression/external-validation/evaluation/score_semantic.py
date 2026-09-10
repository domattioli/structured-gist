#!/usr/bin/env python3
"""
Runs every metric that DOES need a semantic judge's verdicts -- but is
otherwise pure arithmetic -- against the frozen judgments: task-weighted
fact/relation retention (reuses ../scoring/combine.py's score_semantic,
unmodified), SPR + critical-loss diagnostics (reuses ../scoring/spr.py's
score_spr, unmodified), and corrected retained-unit findability (reuses
../scoring/findability.py's alignment/ranking pipeline, unmodified --
mirrors that module's own main() loop, adapted to this corpus's single-
model layout instead of its tier-subdirectory layout).

No model calls in this script. Every number here is deterministic given
the already-frozen derived gold + weights + judged/*.json -- re-running it
reproduces byte-identical output.

Writes one file per dataset: evaluation/<dataset>/scores.json.

Run: python3 score_semantic.py [--dataset qmsum|qasper|hotpotqa|all]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXTERNAL_VALIDATION = Path(__file__).resolve().parent.parent
SCORING = EXTERNAL_VALIDATION.parent / "scoring"
sys.path.insert(0, str(SCORING))
sys.path.insert(0, str(EXTERNAL_VALIDATION / "adapters"))
sys.path.insert(0, str(EXTERNAL_VALIDATION / "scripts"))
import combine  # noqa: E402 -- ../scoring/combine.py
import spr  # noqa: E402 -- ../scoring/spr.py
import findability  # noqa: E402 -- ../scoring/findability.py
from text_norm import tokenize  # noqa: E402
import common  # noqa: E402 -- ../adapters/common.py
from corpus_lib import canonical_json_bytes, read_json  # noqa: E402

LEVELS = ["skim", "standard", "deep"]
DATASETS = ("qmsum", "qasper", "hotpotqa")


def score_findability_for_level(gold: dict, judged_level: dict, source_tokens, rendering_text: str) -> dict:
    """Mirrors findability.py's main() inner loop for one (case, level),
    using this corpus's single native question (q1) instead of the
    hand-built corpus's multi-question convention."""
    source_alignment = findability.align_units_to_source(gold, source_tokens)
    idx = findability.build_rendering_index(rendering_text)
    gist_pos = findability.locate_all_gist_positions(gold, judged_level, idx.tokens)

    retained_strict, excluded_strict = findability.build_retained_units(
        gold, judged_level, source_alignment, gist_pos, findability.STRICT_STATUSES
    )
    retained_explore, excluded_explore = findability.build_retained_units(
        gold, judged_level, source_alignment, gist_pos, findability.EXPLORATORY_STATUSES
    )
    src_ranks_strict = findability.rank_units(retained_strict, "source")
    gist_ranks_strict = findability.rank_units(retained_strict, "gist")
    findability.assert_identical_retained_sets(retained_strict, src_ranks_strict, gist_ranks_strict)
    src_ranks_explore = findability.rank_units(retained_explore, "source")
    gist_ranks_explore = findability.rank_units(retained_explore, "gist")
    findability.assert_identical_retained_sets(retained_explore, src_ranks_explore, gist_ranks_explore)

    question_results = {}
    for q in gold.get("questions", []):
        required_ids = q.get("fact_ids", [])
        unit_rank_strict = findability.score_question_unit_rank(
            required_ids, retained_strict, excluded_strict, src_ranks_strict, gist_ranks_strict
        )
        unit_rank_explore = findability.score_question_unit_rank(
            required_ids, retained_explore, excluded_explore, src_ranks_explore, gist_ranks_explore
        )
        diag_structural = (
            findability.structural_diagnostic(required_ids, gist_pos, idx)
            if unit_rank_strict.get("eligible")
            else None
        )
        question_results[q["id"]] = {
            "type": q["type"],
            "support_unit_count": len(required_ids),
            "unit_rank": {"strict": unit_rank_strict, "exploratory": unit_rank_explore},
            "structural_diagnostic": diag_structural,
        }

    return {
        "source_integrity": {
            "units_total": len(gold.get("facts", [])) + len(gold.get("relations", [])),
            "units_unaligned_in_source": source_alignment.unaligned_unit_ids,
            "units_ambiguous_in_source": source_alignment.ambiguous_unit_ids,
        },
        "retained_set": {
            "strict": {"size": len(retained_strict), "unit_ids": sorted(retained_strict), "excluded": excluded_strict},
            "exploratory": {
                "size": len(retained_explore),
                "unit_ids": sorted(retained_explore),
                "excluded": excluded_explore,
            },
        },
        "questions": question_results,
    }


def score_dataset(dataset: str) -> dict:
    cases_dir = EXTERNAL_VALIDATION / dataset / "cases"
    judgments_dir = EXTERNAL_VALIDATION / "evaluation" / dataset / "judgments"
    renderings_dir = EXTERNAL_VALIDATION / "evaluation" / dataset / "renderings"
    results = {}

    for case_dir in sorted(cases_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        case_id = case_dir.name
        judged_path = judgments_dir / f"{case_id}.json"
        if not judged_path.exists():
            results[case_id] = {"status": "unscorable", "reason": "no judgment file"}
            continue

        judged = read_json(judged_path)
        weights = common.load_blind_weights(dataset, case_id)
        if weights is None:
            results[case_id] = {"status": "unscorable", "reason": "no derived_blind_weights.json"}
            continue

        gold_view = common.to_gold_view(dataset, case_id)
        source_text = (case_dir / "source.md").read_text("utf-8")
        source_tokens = tokenize(source_text)

        results[case_id] = {}
        for level in LEVELS:
            if level not in judged:
                results[case_id][level] = {"status": "unscorable", "reason": f"no '{level}' key in judgment file"}
                continue
            judged_level = judged[level]

            semantic = combine.score_semantic(gold_view, judged_level)
            spr_scores = spr.score_spr(gold_view, judged_level, weights)

            rendering_path = renderings_dir / case_id / f"{level}.md"
            if rendering_path.exists():
                rendering_text = rendering_path.read_text("utf-8")
                findability_scores = score_findability_for_level(gold_view, judged_level, source_tokens, rendering_text)
            else:
                findability_scores = {"status": "unscorable", "reason": "rendering missing"}

            results[case_id][level] = {
                "status": "scored",
                "semantic": semantic,
                "spr": spr_scores,
                "findability": findability_scores,
            }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=[*DATASETS, "all"], default="all")
    args = parser.parse_args()

    targets = list(DATASETS) if args.dataset == "all" else [args.dataset]
    for dataset in targets:
        results = score_dataset(dataset)
        out_path = EXTERNAL_VALIDATION / "evaluation" / dataset / "scores.json"
        out_path.write_bytes(canonical_json_bytes(results))
        n_scored = sum(
            1
            for levels in results.values()
            if isinstance(levels, dict)
            for r in levels.values()
            if isinstance(r, dict) and r.get("status") == "scored"
        )
        print(f"[{dataset}] {len(results)} cases, {n_scored} (case,level) scored -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
